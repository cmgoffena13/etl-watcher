import logging

import pendulum
from fastapi import Response
from sqlalchemy import func, select, text, update
from sqlmodel import Session

from src.database.models.pipeline import Pipeline
from src.database.models.pipeline_execution import PipelineExecution
from src.database.models.timeliness_pipeline_execution_log import (
    TimelinessPipelineExecutionLog,
)
from src.database.pipeline_utils import db_get_or_create_pipeline
from src.models.pipeline import PipelinePostInput, PipelinePostOutput
from src.notifier import AlertLevel, send_slack_message

logger = logging.getLogger(__name__)


async def db_check_timeliness(session: Session, response: Response):
    pipeline_status = await db_check_pipeline_timeliness(session)
    execution_status = await db_check_pipeline_execution_timeliness(session, response)
    if pipeline_status == "warning" or execution_status == "warning":
        return {"status": "warning"}
    else:
        return {"status": "success"}


async def db_check_pipeline_timeliness(session: Session):
    timestamp = pendulum.now("UTC")

    await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))

    pipelines_query = text("""
        WITH CTE AS (
            SELECT
                cte_p.id as pipeline_id,
                cte_pt.timely_number,
                cte_pt.timely_datepart
            FROM pipeline_type AS cte_pt
            INNER JOIN pipeline AS cte_p
                ON cte_p.pipeline_type_id = cte_pt.id
            WHERE cte_pt.mute_timely_check = false
        )
        SELECT
            p.id as pipeline_id,
            p.name as pipeline_name,
            p.last_target_insert,
            p.last_target_update,
            p.last_target_soft_delete,
            p.timely_number as child_timely_number,
            p.timely_datepart as child_timely_datepart,
            pt.timely_number as parent_timely_number,
            pt.timely_datepart as parent_timely_datepart
        INTO TEMP TABLE check_pipeline_timeliness_temp
        FROM pipeline AS p
        INNER JOIN CTE AS pt
            ON pt.pipeline_id = p.id
        WHERE p.mute_timely_check = false
    """)
    await session.exec(pipelines_query)

    pipelines_query = text("""
        SELECT
            pipeline_id,
            pipeline_name,
            last_target_insert,
            last_target_update,
            last_target_soft_delete,
            child_timely_number,
            child_timely_datepart,
            parent_timely_number,
            parent_timely_datepart
        FROM check_pipeline_timeliness_temp
    """)

    pipelines = (await session.exec(pipelines_query)).fetchall()

    logger.info(f"Processing {len(pipelines)} pipelines for timeliness check")

    fail_results = []

    for pipeline in pipelines:
        (
            pipeline_id,
            pipeline_name,
            last_insert,
            last_update,
            last_delete,
            child_number,
            child_datepart,
            parent_number,
            parent_datepart,
        ) = pipeline

        max_dml = None
        for ts in [last_insert, last_update, last_delete]:
            if ts is not None:
                if max_dml is None or ts > max_dml:
                    max_dml = ts

        if max_dml is None:
            continue

        if child_datepart and child_number:
            timely_datepart = child_datepart
            timely_number = child_number
        elif parent_datepart and parent_number:
            timely_datepart = parent_datepart
            timely_number = parent_number
        else:
            logger.warning(
                f"Pipeline {pipeline_id} ({pipeline_name}) skipped - incomplete timely settings "
                f"(child: {child_datepart}, {child_number}; parent: {parent_datepart}, {parent_number})"
            )
            continue

        # Calculate threshold time
        calculated_time = _calculate_timely_time(
            max_dml, timely_datepart, timely_number
        )

        if calculated_time < timestamp:
            display_datepart = _get_display_datepart(timely_datepart, timely_number)

            fail_results.append(
                {
                    "pipeline_id": pipeline_id,
                    "pipeline_name": pipeline_name,
                    "last_dml": max_dml,
                    "timely_number": timely_number,
                    "timely_datepart": display_datepart,
                }
            )

            logger.warning(
                f"Pipeline {pipeline_id} ({pipeline_name}) failed timeliness check"
            )

    if fail_results:
        logger.warning(
            f"Pipeline Timeliness Check Failed - {len(fail_results)} pipeline(s) overdue"
        )
        await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))

        try:
            pipeline_details = []
            for result in fail_results:
                pipeline_details.append(
                    f"\t• {result['pipeline_name']} (ID: {result['pipeline_id']}): "
                    f"Last DML {result['last_dml']}, Expected within {result['timely_number']} {result['timely_datepart']}"
                )

            send_slack_message(
                level=AlertLevel.WARNING,
                title="Timeliness Check - Pipeline DML",
                message=f"Pipeline Timeliness Check Failed - {len(fail_results)} pipeline(s) overdue",
                details={
                    "Failed Pipelines": "\n" + "\n".join(pipeline_details),
                    "Total Overdue": len(fail_results),
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to send Slack notification for timeliness failures: {e}"
            )
        return "warning"
    else:
        logger.info("All pipelines passed timeliness check")
        await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))

    return "success"


def _calculate_timely_time(max_dml, datepart, number):
    """Calculate the expected time based on datepart and number"""
    # Convert to pendulum if it's a regular datetime
    if hasattr(max_dml, "add"):
        dml_time = max_dml
    else:
        dml_time = pendulum.instance(max_dml)

    if datepart.upper() == "MINUTE":
        return dml_time.add(minutes=number)
    elif datepart.upper() == "HOUR":
        return dml_time.add(hours=number)
    elif datepart.upper() == "DAY":
        return dml_time.add(days=number)
    elif datepart.upper() == "WEEK":
        return dml_time.add(weeks=number)
    elif datepart.upper() == "MONTH":
        return dml_time.add(months=number)
    elif datepart.upper() == "YEAR":
        return dml_time.add(years=number)
    else:
        raise ValueError(f"Unsupported datepart: {datepart}")


def _get_display_datepart(datepart, number):
    """Convert datepart to display format (singular/plural)"""
    datepart_lower = datepart.lower()
    if number == 1:
        return datepart_lower
    else:
        return f"{datepart_lower}s"


async def db_check_pipeline_execution_timeliness(session: Session, response: Response):
    # Create Initial Timeliness Pipeline. Does not overwrite threshold if already exists.
    pipeline_input = PipelinePostInput(
        name="Timeliness Check",
        pipeline_type_name="Audit",
        pipeline_type_group_name="Internal",
        pipeline_args={"timeliness_execution_seconds_threshold": 1800},
    )

    pipeline = PipelinePostOutput(
        **await db_get_or_create_pipeline(
            session=session, pipeline=pipeline_input, response=response
        )
    )

    logger.info("Starting Pipeline Execution Timeliness Check")
    timestamp = pendulum.now("UTC")
    next_watermark = (
        await session.exec(
            select(func.max(PipelineExecution.id)).where(
                PipelineExecution.end_date <= timestamp,
                PipelineExecution.end_date.is_not(None),
            )
        )
    ).scalar_one()

    update_stmt = (
        update(Pipeline)
        .where(Pipeline.id == pipeline.id)
        .values(next_watermark=str(next_watermark))
        .returning(Pipeline.watermark, Pipeline.pipeline_args)
    )
    watermark, pipeline_args = (await session.exec(update_stmt)).first()
    await session.commit()

    if watermark is None:
        watermark = int(0)
    else:
        watermark = int(watermark)

    seconds_threshold = pipeline_args.get(
        "timeliness_execution_seconds_threshold", 1800
    )

    await session.exec(
        text("DROP TABLE IF EXISTS timeliness_pipeline_execution_log_temp")
    )

    cte_query = text("""
        WITH CTE AS (
            SELECT id
            FROM pipeline_execution
            WHERE id > :watermark
                AND id <= :next_watermark
        )
        SELECT
            pe.id,
            pe.pipeline_id,
            pe.duration_seconds
        INTO TEMP TABLE timeliness_pipeline_execution_log_temp
        FROM pipeline_execution AS pe
        INNER JOIN CTE
            ON CTE.id = pe.id
        WHERE pe.duration_seconds > :seconds_threshold
    """)

    # Execute the query with parameters
    await session.exec(
        cte_query,
        params={
            "watermark": watermark,
            "next_watermark": next_watermark,
            "seconds_threshold": seconds_threshold,
        },
    )

    insert_query = text("""
        INSERT INTO timeliness_pipeline_execution_log (pipeline_execution_id, pipeline_id, duration_seconds, seconds_threshold)
        SELECT
            id,
            pipeline_id,
            duration_seconds,
            :seconds_threshold
        FROM timeliness_pipeline_execution_log_temp AS r
        WHERE NOT EXISTS (
            SELECT 1
            FROM timeliness_pipeline_execution_log AS t
            WHERE t.pipeline_execution_id = r.id
        )
    """)

    result = await session.exec(
        insert_query, params={"seconds_threshold": seconds_threshold}
    )
    rows_inserted = result.rowcount

    await session.exec(
        text("DROP TABLE IF EXISTS timeliness_pipeline_execution_log_temp")
    )

    update_stmt = (
        update(Pipeline)
        .where(Pipeline.id == pipeline.id)
        .values(watermark=str(next_watermark))
    )
    await session.exec(update_stmt)
    await session.commit()

    logger.info(
        f"Inserted {rows_inserted} new timeliness pipeline execution log records"
    )

    if rows_inserted > 0:
        logger.warning(
            f"Found {rows_inserted} pipeline execution(s) exceeding timeliness threshold"
        )
        try:
            affected_pipelines_query = (
                select(
                    TimelinessPipelineExecutionLog.pipeline_execution_id,
                    TimelinessPipelineExecutionLog.pipeline_id,
                    Pipeline.name,
                    TimelinessPipelineExecutionLog.duration_seconds,
                )
                .join(
                    Pipeline, Pipeline.id == TimelinessPipelineExecutionLog.pipeline_id
                )
                .where(
                    TimelinessPipelineExecutionLog.pipeline_execution_id > watermark,
                    TimelinessPipelineExecutionLog.pipeline_execution_id
                    <= next_watermark,
                )
            )

            affected_pipelines = (await session.exec(affected_pipelines_query)).all()

            pipeline_details = []
            for (
                pipeline_execution_id,
                pipeline_id,
                pipeline_name,
                duration_seconds,
            ) in affected_pipelines:
                pipeline_details.append(
                    f"\t• Pipeline Execution ID: {pipeline_execution_id} - '{pipeline_name}' (ID: {pipeline_id}): {duration_seconds} seconds"
                )

            send_slack_message(
                level=AlertLevel.WARNING,
                title="Timeliness Check - Pipeline Execution",
                message=f"Found {rows_inserted} pipeline execution(s) exceeding timeliness threshold",
                details={
                    "Threshold (seconds)": seconds_threshold,
                    "Affected Pipelines": "\n" + "\n".join(pipeline_details),
                },
            )

            return "warning"
        except Exception as e:
            logger.error(
                f"Failed to send Slack notification for timeliness executions: {e}"
            )
    return "success"

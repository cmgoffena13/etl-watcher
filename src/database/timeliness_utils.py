import logging

import pendulum
from fastapi import HTTPException, Response
from sqlalchemy import func, select, text, update
from sqlmodel import Session

from src.database.models.pipeline import Pipeline
from src.database.models.pipeline_execution import PipelineExecution
from src.database.pipeline_utils import db_get_or_create_pipeline
from src.models.pipeline import PipelinePostInput, PipelinePostOutput

logger = logging.getLogger(__name__)


async def db_check_timeliness(session: Session, response: Response):
    await db_check_pipeline_timeliness(session)
    await db_check_pipeline_execution_timeliness(session, response)
    return {"status": "success"}


async def db_check_pipeline_timeliness(session: Session):
    timestamp = pendulum.now("UTC")

    await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))

    pipelines_query = text("""
        WITH CTE AS (
            SELECT
                p.id as pipeline_id,
                pt.timely_number,
                pt.timely_datepart
            FROM pipeline_type AS pt
            INNER JOIN pipeline AS p
                ON p.pipeline_type_id = pt.id
            WHERE pt.mute_timely_check = false
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
        error_message = _generate_timeliness_error_message(fail_results)
        logger.error(f"Timeliness check failed: {error_message}")

        await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))

        raise HTTPException(status_code=500, detail=error_message)
    else:
        logger.info("All pipelines passed timeliness check")
        await session.exec(text("DROP TABLE IF EXISTS check_pipeline_timeliness_temp"))


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


def _generate_timeliness_error_message(fail_results):
    """Generate error message for failed timeliness checks"""
    error_parts = ["The following Pipelines failed their timeliness checks:"]

    for result in fail_results:
        error_parts.append(
            f"{result['pipeline_id']}: '{result['pipeline_name']}' has not had a DML operation "
            f"within the timeframe: {result['timely_number']} {result['timely_datepart']}; "
            f"Last DML Operation: {result['last_dml']};"
        )
    return "\n".join(error_parts)


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

    await session.exec(
        text("DROP TABLE IF EXISTS timeliness_pipeline_execution_log_temp")
    )

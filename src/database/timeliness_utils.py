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


async def db_check_pipeline_execution_timeliness(session: Session, response: Response):
    # Create Initial Timeliness Pipeline. Does not overwrite threshold if already exists.
    pipeline_input = PipelinePostInput(
        name="Timeliness Check",
        pipeline_type_name="Audit",
        pipeline_type_group_name="Internal",
        pipeline_metadata={"timeliness_execution_seconds_threshold": 1800},
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
        .returning(Pipeline.watermark, Pipeline.pipeline_metadata)
    )
    watermark, pipeline_metadata = (await session.exec(update_stmt)).first()
    await session.commit()

    if watermark is None:
        watermark = int(0)
    else:
        watermark = int(watermark)

    seconds_threshold = pipeline_metadata.get(
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

            return {"status": "warning"}
        except Exception as e:
            logger.error(
                f"Failed to send Slack notification for timeliness executions: {e}"
            )
    return {"status": "success"}

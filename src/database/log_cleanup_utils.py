import asyncio
import logging

import pendulum
from sqlalchemy import func, select, text
from sqlmodel import Session

from src.database.models.pipeline_execution import PipelineExecution
from src.models.log_cleanup import LogCleanupPostInput

logger = logging.getLogger(__name__)


async def db_log_cleanup(session: Session, config: LogCleanupPostInput):
    current_date = pendulum.now("UTC").date()
    retention_date = current_date.subtract(days=config.retention_days)
    batch_size = config.batch_size

    # One off pattern to delete freshness pipeline logs
    freshness_delete_query = """
    WITH CTE AS (
    SELECT id
    FROM {table_name}
    WHERE {filter_column} <= :retention_date
    LIMIT :batch_size
    )
    DELETE FROM {table_name}
    USING CTE
    WHERE {table_name}.id = CTE.id
    """

    formatted_delete_query = freshness_delete_query.format(
        table_name="freshness_pipeline_log",
        filter_column="last_dml_timestamp",
    )

    total_freshness_pipeline_logs_deleted = 0
    while True:
        result = await session.exec(
            text(formatted_delete_query).bindparams(
                batch_size=batch_size, retention_date=retention_date
            )
        )

        if result.rowcount == 0:
            break
            total_freshness_pipeline_logs_deleted += result.rowcount

    # Pattern for exeuction dependent logs
    max_pipeline_execution_id = (
        await session.exec(
            select(func.max(PipelineExecution.id)).where(
                PipelineExecution.start_date <= retention_date
            )
        )
    ).scalar_one()

    delete_query = """
    WITH CTE AS (
    SELECT {id_column}
    FROM {table_name}
    WHERE {filter_column} <= :max_pipeline_execution_id
    LIMIT :batch_size
    )
    DELETE FROM {table_name}
    USING CTE
    WHERE {table_name}.{id_column} = CTE.{id_column}
    """

    table_infos = [
        {
            "table_name": "timeliness_pipeline_execution_log",
            "filter_column": "pipeline_execution_id",
            "total_timeliness_pipeline_execution_logs_deleted": 0,
            "id_column": "pipeline_execution_id",
        },
        {
            "table_name": "anomaly_detection_result",
            "filter_column": "pipeline_execution_id",
            "total_anomaly_detection_results_deleted": 0,
            "id_column": "pipeline_execution_id",
        },
        {  # Make sure this is last because foreign key constraints
            "table_name": "pipeline_execution",
            "filter_column": "id",
            "total_pipeline_executions_deleted": 0,
            "id_column": "id",
        },
    ]

    for table_info in table_infos:
        name = "total_" + table_info["table_name"] + "s_deleted"
        while True:
            formatted_query = delete_query.format(
                table_name=table_info["table_name"],
                filter_column=table_info["filter_column"],
                id_column=table_info["id_column"],
            )
            result = await session.exec(
                text(formatted_query).bindparams(
                    max_pipeline_execution_id=max_pipeline_execution_id,
                    batch_size=batch_size,
                )
            )
            if result.rowcount == 0:
                break
            table_info[name] += result.rowcount

            # Small delay between batches to reduce database pressure
            await asyncio.sleep(0.1)

    return {
        "total_timeliness_pipeline_execution_logs_deleted": table_infos[0][
            "total_timeliness_pipeline_execution_logs_deleted"
        ],
        "total_anomaly_detection_results_deleted": table_infos[1][
            "total_anomaly_detection_results_deleted"
        ],
        "total_pipeline_executions_deleted": table_infos[2][
            "total_pipeline_executions_deleted"
        ],
        "total_freshness_pipeline_logs_deleted": total_freshness_pipeline_logs_deleted,
    }

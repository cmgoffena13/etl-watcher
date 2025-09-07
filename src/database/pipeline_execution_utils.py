import logging

from sqlmodel import Integer, Session, case, func, literal, update

from src.database.models import Pipeline, PipelineExecution
from src.models.pipeline_execution import (
    PipelineExecutionEndInput,
    PipelineExecutionStartInput,
    PipelineExecutionStartOutput,
)

logger = logging.getLogger(__name__)


async def db_start_pipeline_execution(
    pipeline_execution: PipelineExecutionStartInput,
    session: Session,
) -> PipelineExecutionStartOutput:
    execution_start_stmt = (
        PipelineExecution.__table__.insert()
        .returning(PipelineExecution.id)
        .values(**pipeline_execution.model_dump(exclude_unset=True))
    )
    pipeline_execution_id = (await session.exec(execution_start_stmt)).scalar_one()
    await session.commit()
    return {"id": pipeline_execution_id}


async def db_end_pipeline_execution(
    pipeline_execution: PipelineExecutionEndInput,
    session: Session,
) -> None:
    pipeline_execution = PipelineExecution(
        **pipeline_execution.model_dump(exclude_unset=True)
    )

    # Transaction Handling
    async with session.begin():
        # Update Pipeline Execution record with completion details
        execution_update_stmt = (
            update(PipelineExecution)
            .where(PipelineExecution.id == pipeline_execution.id)
            .values(
                **pipeline_execution.model_dump(exclude={"id"}, exclude_unset=True),
                duration_seconds=func.extract(
                    "epoch", pipeline_execution.end_date - PipelineExecution.start_date
                ).cast(Integer),
            )
            .returning(PipelineExecution.pipeline_id)
        )
        pipeline_id = (await session.exec(execution_update_stmt)).scalar_one()

        pipeline_execution_inserts = pipeline_execution.inserts or 0
        pipeline_execution_updates = pipeline_execution.updates or 0
        pipeline_execution_soft_deletes = pipeline_execution.soft_deletes or 0

        # Update Pipeline record with latest DML info
        pipeline_update_stmt = (
            update(Pipeline)
            .where(Pipeline.id == pipeline_id)
            .values(
                watermark=Pipeline.next_watermark,
                last_target_insert=case(
                    (pipeline_execution_inserts > 0, pipeline_execution.end_date),
                    else_=Pipeline.last_target_insert,
                ),
                last_target_update=case(
                    (pipeline_execution_updates > 0, pipeline_execution.end_date),
                    else_=Pipeline.last_target_update,
                ),
                last_target_soft_delete=case(
                    (pipeline_execution_soft_deletes > 0, pipeline_execution.end_date),
                    else_=Pipeline.last_target_soft_delete,
                ),
                load_lineage=False,
            )
        )
        await session.exec(pipeline_update_stmt)

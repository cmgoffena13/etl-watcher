import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Integer, Session, case, func, select, update

from src.database.models import Pipeline, PipelineExecution, PipelineExecutionClosure
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
        .values(
            **pipeline_execution.model_dump(
                exclude_unset=True,
            ),
            hour_recorded=pipeline_execution.start_date.in_timezone("UTC").hour,
            date_recorded=pipeline_execution.start_date.in_timezone("UTC").date(),
        )
    )
    pipeline_execution_id = (await session.exec(execution_start_stmt)).scalar_one()
    await session.commit()

    return {"id": pipeline_execution_id}


async def db_end_pipeline_execution(
    pipeline_execution: PipelineExecutionEndInput,
    session: Session,
) -> int:
    pipeline_execution = PipelineExecution(
        **pipeline_execution.model_dump(exclude_unset=True)
    )

    # Transaction Handling
    async with session.begin():
        # Calculate duration in seconds
        duration_seconds = func.extract(
            "epoch", pipeline_execution.end_date - PipelineExecution.start_date
        ).cast(Integer)

        # Update Pipeline Execution record with completion details
        execution_update_stmt = (
            update(PipelineExecution)
            .where(PipelineExecution.id == pipeline_execution.id)
            .values(
                **pipeline_execution.model_dump(exclude={"id"}, exclude_unset=True),
                duration_seconds=duration_seconds,
                throughput=func.round(
                    case(
                        (
                            duration_seconds > 0,
                            pipeline_execution.total_rows / duration_seconds,
                        ),
                        else_=0,
                    ),
                    4,
                ),
            )
            .returning(PipelineExecution.pipeline_id)
        )

        try:
            pipeline_id = (await session.exec(execution_update_stmt)).scalar_one()
        except NoResultFound as e:
            logger.error(f"Pipeline execution not found: {e}")
            raise HTTPException(status_code=404, detail="Pipeline execution not found")
        except IntegrityError as e:
            if (
                "check constraint" in str(e).lower()
                and "pipeline_execution_check" in str(e).lower()
            ):
                raise HTTPException(
                    status_code=400, detail="end_date must be greater than start_date"
                )
            else:
                logger.error(f"Database integrity error: {e}")
                raise HTTPException(status_code=500, detail="Database integrity error")

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

    return pipeline_id


async def db_maintain_pipeline_execution_closure_table(
    session: Session, execution_id: int, parent_id: Optional[int]
) -> None:
    """Maintain the closure table when a new execution is created."""
    # Add self-reference (depth 0)
    self_reference = PipelineExecutionClosure(
        parent_execution_id=execution_id, child_execution_id=execution_id, depth=0
    )
    session.add(self_reference)

    # If there's a parent, copy all ancestor relationships and increment depth by 1
    if parent_id:
        # Get all ancestor relationships from parent
        parent_relationships = await session.exec(
            select(PipelineExecutionClosure).where(
                PipelineExecutionClosure.child_execution_id == parent_id
            )
        )

        # Create new relationships for this execution
        for relationship in parent_relationships:
            new_relationship = PipelineExecutionClosure(
                parent_execution_id=relationship.parent_execution_id,
                child_execution_id=execution_id,
                depth=relationship.depth + 1,
            )
            session.add(new_relationship)

    await session.commit()

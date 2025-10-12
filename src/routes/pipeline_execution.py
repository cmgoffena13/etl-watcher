from fastapi import APIRouter, status

from src.celery_tasks import (
    detect_anomalies_task,
    pipeline_execution_closure_maintain_task,
)
from src.database.pipeline_execution_utils import (
    db_end_pipeline_execution,
    db_get_pipeline_execution,
    db_start_pipeline_execution,
)
from src.database.session import SessionDep
from src.models.pipeline_execution import (
    PipelineExecutionEndInput,
    PipelineExecutionGetOutput,
    PipelineExecutionStartInput,
    PipelineExecutionStartOutput,
)

router = APIRouter()


@router.post(
    "/start_pipeline_execution",
    response_model=PipelineExecutionStartOutput,
    status_code=status.HTTP_201_CREATED,
)
async def start_pipeline_execution(
    pipeline_execution: PipelineExecutionStartInput,
    session: SessionDep,
):
    result = await db_start_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )

    # Queue closure table maintenance task
    pipeline_execution_closure_maintain_task.delay(
        execution_id=result["id"], parent_id=pipeline_execution.parent_id
    )

    return result


@router.post("/end_pipeline_execution", status_code=status.HTTP_204_NO_CONTENT)
async def end_pipeline_execution(
    pipeline_execution: PipelineExecutionEndInput,
    session: SessionDep,
):
    pipeline_id = await db_end_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )

    # Queue anomaly detection as a Celery task for faster response
    if pipeline_execution.completed_successfully:
        detect_anomalies_task.delay(
            pipeline_id=pipeline_id,
            pipeline_execution_id=pipeline_execution.id,
        )


@router.get(
    "/pipeline_execution/{pipeline_execution_id}",
    response_model=PipelineExecutionGetOutput,
)
async def get_pipeline_execution(
    pipeline_execution_id: int,
    session: SessionDep,
):
    return await db_get_pipeline_execution(
        pipeline_execution_id=pipeline_execution_id,
        session=session,
    )

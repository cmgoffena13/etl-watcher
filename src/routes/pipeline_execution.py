from fastapi import APIRouter, status

from src.database.anomaly_detection_utils import db_detect_anomalies_for_pipeline
from src.database.pipeline_execution_utils import (
    db_end_pipeline_execution,
    db_start_pipeline_execution,
)
from src.database.session import SessionDep
from src.models.pipeline_execution import (
    PipelineExecutionEndInput,
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
    return await db_start_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )


@router.post("/end_pipeline_execution", status_code=status.HTTP_204_NO_CONTENT)
async def end_pipeline_execution(
    pipeline_execution: PipelineExecutionEndInput,
    session: SessionDep,
):
    await db_end_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )
    await db_detect_anomalies_for_pipeline(
        session=session,
        pipeline_id=pipeline_execution.pipeline_id,
        pipeline_execution_id=pipeline_execution.id,
    )

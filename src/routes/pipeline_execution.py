from fastapi import APIRouter, Response

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


@router.post("/start_pipeline_execution", response_model=PipelineExecutionStartOutput)
async def start_pipeline_execution(
    pipeline_execution: PipelineExecutionStartInput,
    session: SessionDep,
):
    return await db_start_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )


@router.post("/end_pipeline_execution")
async def end_pipeline_execution(
    pipeline_execution: PipelineExecutionEndInput,
    session: SessionDep,
):
    await db_end_pipeline_execution(
        pipeline_execution=pipeline_execution, session=session
    )

from fastapi import APIRouter, Response

from src.database.pipeline import Pipeline, get_or_create_pipeline, update_pipeline
from src.database.session import SessionDep
from src.models.pipeline import (
    PipelineIDGetInput,
    PipelineIDGetOutput,
    PipelinePatchInput,
    PipelinePostInput,
    PipelinePostOutput,
)

router = APIRouter()


@router.post("/pipeline", response_model=PipelinePostOutput)
async def create_pipeline(
    pipeline: PipelinePostInput, response: Response, session: SessionDep
):
    return await get_or_create_pipeline(
        session=session, pipeline=pipeline, response=response
    )


@router.get("/pipeline_id", response_model=PipelineIDGetOutput)
async def get_pipeline_id(
    pipeline: PipelineIDGetInput, response: Response, session: SessionDep
):
    return await get_or_create_pipeline(
        session=session, pipeline=pipeline, response=response
    )


@router.patch("/pipeline", response_model=Pipeline)
async def patch_pipeline(pipeline: PipelinePatchInput, session: SessionDep):
    return await update_pipeline(session=session, patch=pipeline)

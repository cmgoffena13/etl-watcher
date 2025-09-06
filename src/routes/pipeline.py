from fastapi import APIRouter, Response
from sqlalchemy import select

from src.database.pipeline import Pipeline, db_get_or_create_pipeline, update_pipeline
from src.database.session import SessionDep
from src.models.pipeline import (
    PipelinePatchInput,
    PipelinePostInput,
    PipelinePostOutput,
)

router = APIRouter()


@router.post("/pipeline", response_model=PipelinePostOutput)
async def get_or_create_pipeline(
    pipeline: PipelinePostInput, response: Response, session: SessionDep
):
    return await db_get_or_create_pipeline(
        session=session, pipeline=pipeline, response=response
    )


@router.get("/pipeline", response_model=list[Pipeline])
async def get_pipelines(session: SessionDep):
    result = await session.exec(select(Pipeline))
    return result.scalars().all()


@router.patch("/pipeline", response_model=Pipeline)
async def update_pipeline(pipeline: PipelinePatchInput, session: SessionDep):
    return await update_pipeline(session=session, patch=pipeline)

from fastapi import APIRouter, Response, status
from sqlalchemy import select

from src.database.models.pipeline import Pipeline
from src.database.pipeline_utils import db_get_or_create_pipeline, db_update_pipeline
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


@router.get("/pipeline", response_model=list[Pipeline], status_code=status.HTTP_200_OK)
async def get_pipelines(session: SessionDep):
    return (await session.exec(select(Pipeline))).scalars().all()


@router.get(
    "/pipeline/{pipeline_id}", response_model=Pipeline, status_code=status.HTTP_200_OK
)
async def get_pipeline(pipeline_id: int, session: SessionDep):
    return (
        await session.exec(select(Pipeline).where(Pipeline.id == pipeline_id))
    ).scalar_one_or_none()


@router.patch("/pipeline", response_model=Pipeline, status_code=status.HTTP_200_OK)
async def update_pipeline(pipeline: PipelinePatchInput, session: SessionDep):
    return await db_update_pipeline(session=session, patch=pipeline)

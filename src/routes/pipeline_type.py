from fastapi import APIRouter, Response
from sqlalchemy import select

from src.database.pipeline_type import (
    PipelineType,
    get_or_create_pipeline_type,
    update_pipeline_type,
)
from src.database.session import SessionDep
from src.models.pipeline_type import (
    PipelineTypePatchInput,
    PipelineTypePostInput,
    PipelineTypePostOutput,
)

router = APIRouter()


@router.post("/pipeline_type", response_model=PipelineTypePostOutput)
async def create_pipeline_type(
    pipeline_type: PipelineTypePostInput, response: Response, session: SessionDep
):
    return await get_or_create_pipeline_type(
        session=session, pipeline_type=pipeline_type, response=response
    )


@router.get("/pipeline_type", response_model=list[PipelineType])
async def get_pipeline_types(session: SessionDep):
    result = await session.exec(select(PipelineType))
    return result.scalars().all()


@router.patch("/pipeline_type", response_model=PipelineType)
async def update_pipeline_type(
    pipeline_type: PipelineTypePatchInput, session: SessionDep
):
    return await update_pipeline_type(patch=pipeline_type, session=session)

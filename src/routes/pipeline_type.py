from fastapi import APIRouter, Response, status
from sqlalchemy import select

from src.database.models.pipeline_type import PipelineType
from src.database.pipeline_type_utils import (
    db_get_or_create_pipeline_type,
    db_update_pipeline_type,
)
from src.database.session import SessionDep
from src.models.pipeline_type import (
    PipelineTypePatchInput,
    PipelineTypePostInput,
    PipelineTypePostOutput,
)

router = APIRouter()


@router.post("/pipeline_type", response_model=PipelineTypePostOutput)
async def get_or_create_pipeline_type(
    pipeline_type: PipelineTypePostInput, response: Response, session: SessionDep
):
    return await db_get_or_create_pipeline_type(
        session=session, pipeline_type=pipeline_type, response=response
    )


@router.get(
    "/pipeline_type", response_model=list[PipelineType], status_code=status.HTTP_200_OK
)
async def get_pipeline_types(session: SessionDep):
    return (await session.exec(select(PipelineType))).scalars().all()


@router.patch(
    "/pipeline_type", response_model=PipelineType, status_code=status.HTTP_200_OK
)
async def update_pipeline_type(
    pipeline_type: PipelineTypePatchInput, session: SessionDep
):
    return await db_update_pipeline_type(patch=pipeline_type, session=session)

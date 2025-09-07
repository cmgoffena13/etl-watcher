import logging

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlmodel import Session

from src.database.models.pipeline_type import PipelineType
from src.models.pipeline_type import (
    PipelineTypePatchInput,
    PipelineTypePostInput,
    PipelineTypePostOutput,
)

logger = logging.getLogger(__name__)


async def db_get_or_create_pipeline_type(
    session: Session, pipeline_type: PipelineTypePostInput, response: Response
) -> PipelineTypePostOutput:
    """Get existing pipeline type id or create new one and return id"""
    created = False

    pipeline_type_id = (
        await session.exec(
            select(PipelineType.id).where(PipelineType.name == pipeline_type.name)
        )
    ).scalar_one_or_none()

    if pipeline_type_id is None:
        logger.info(f"Pipeline '{pipeline_type.name}' Not Found. Creating...")
        stmt = (
            PipelineType.__table__.insert()
            .returning(PipelineType.id)
            .values(**pipeline_type.model_dump(exclude={"id"}))
        )
        pipeline_type_id = (await session.exec(stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(f"Pipeline Type '{pipeline_type.name}' Successfully Created")

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": pipeline_type_id}


async def db_update_pipeline_type(
    session: Session, patch: PipelineTypePatchInput
) -> PipelineType:
    pipeline_type = (
        await session.exec(select(PipelineType).where(PipelineType.id == patch.id))
    ).scalar_one_or_none()
    if pipeline_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline Type Not Found"
        )

    pipeline_type.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        if field == "id":
            continue
        setattr(pipeline_type, field, value)

    session.add(pipeline_type)
    await session.commit()
    await session.refresh(pipeline_type)
    return pipeline_type

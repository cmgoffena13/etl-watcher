import logging

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import select, update
from sqlmodel import Session

from src.database.models.pipeline import Pipeline
from src.database.pipeline_type_utils import db_get_or_create_pipeline_type
from src.models.pipeline import (
    PipelinePatchInput,
    PipelinePostInput,
    PipelinePostOutput,
)
from src.models.pipeline_type import PipelineTypePostInput, PipelineTypePostOutput

logger = logging.getLogger(__name__)


async def db_get_or_create_pipeline(
    session: Session, pipeline: PipelinePostInput, response: Response
) -> PipelinePostOutput:
    """Get existing pipeline id or create new one and return id"""
    created = False
    pipeline_id = None
    active = None
    load_lineage = None
    watermark = None
    new_pipeline = Pipeline(**pipeline.model_dump(exclude_unset=True))

    # Check if Pipeline record exists
    row = (
        await session.exec(
            select(Pipeline.id, Pipeline.active, Pipeline.load_lineage).where(
                Pipeline.name == pipeline.name
            )
        )
    ).one_or_none()

    if row is None:
        logger.info(f"Pipeline '{new_pipeline.name}' Not Found. Creating...")

        # Resolve Pipeline Type Info
        pipeline_type_input = PipelineTypePostInput(name=pipeline.pipeline_type_name)
        pipeline_type = PipelineTypePostOutput(
            **await db_get_or_create_pipeline_type(
                session=session, pipeline_type=pipeline_type_input, response=response
            )
        )

        # Create Pipeline Record
        pipeline_stmt = (
            Pipeline.__table__.insert()
            .returning(Pipeline.id, Pipeline.active, Pipeline.load_lineage)
            .values(
                **new_pipeline.model_dump(exclude={"id"}),
                pipeline_type_id=pipeline_type.id,
            )
        )
        new_row = (await session.exec(pipeline_stmt)).one()
        await session.commit()

        created = True
        pipeline_id = new_row.id
        active = new_row.active
        load_lineage = new_row.load_lineage

        logger.info(f"Pipeline '{pipeline.name}' Successfully Created")
    else:
        pipeline_id = row.id
        active = row.active
        load_lineage = row.load_lineage

        # Update Next Watermark
        if pipeline.next_watermark is not None:
            logger.info("Next WaterMark Provided. Updating and Providing WaterMark...")
            update_stmt = (
                update(Pipeline)
                .where(Pipeline.id == pipeline_id)
                .values(next_watermark=pipeline.next_watermark)
                .returning(Pipeline.watermark)
            )
            watermark = (await session.exec(update_stmt)).scalar_one()
            await session.commit()
            logger.info("Updated with Next WaterMark")

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {
        "id": pipeline_id,
        "active": active,
        "load_lineage": load_lineage,
        "watermark": watermark,
    }


async def db_update_pipeline(session: Session, patch: PipelinePatchInput) -> Pipeline:
    pipeline = (
        await session.exec(select(Pipeline).where(Pipeline.id == patch.id))
    ).scalar_one_or_none()
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline Not Found"
        )

    pipeline.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        if field == "id":
            continue
        setattr(pipeline, field, value)

    session.add(pipeline)
    await session.commit()
    await session.refresh(pipeline)
    return pipeline

import json
import logging

import pendulum
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, Response, status
from sqlalchemy import select, update
from sqlmodel import Session

from src.database.models.anomaly_detection import AnomalyDetectionRule
from src.database.models.pipeline import Pipeline
from src.database.pipeline_type_utils import db_get_or_create_pipeline_type
from src.models.pipeline import (
    PipelinePatchInput,
    PipelinePostInput,
    PipelinePostOutput,
)
from src.models.pipeline_type import PipelineTypePostInput, PipelineTypePostOutput
from src.settings import config
from src.types import AnomalyMetricFieldEnum

logger = logging.getLogger(__name__)


def generate_input_hash(pipeline_input: PipelinePostInput) -> str:
    """Generate a hash of the POST input data for change detection.

    This detects when the hardcoded pipeline data in the pipeline code changes.
    Excludes next_watermark as it's dynamic and changes between executions.
    """
    return str(
        hash(
            json.dumps(
                pipeline_input.model_dump(
                    exclude_unset=True, exclude={"next_watermark"}
                ),
                sort_keys=True,
                default=str,
            )
        )
    )


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

    # Generate hash of the input data
    input_hash = generate_input_hash(pipeline)

    # Check if Pipeline record exists
    row = (
        await session.exec(
            select(
                Pipeline.id, Pipeline.active, Pipeline.load_lineage, Pipeline.input_hash
            ).where(Pipeline.name == pipeline.name)
        )
    ).one_or_none()

    if row is None:
        logger.info(f"Pipeline '{new_pipeline.name}' Not Found. Creating...")

        # Resolve Pipeline Type Info
        pipeline_type_input = PipelineTypePostInput(
            name=pipeline.pipeline_type_name,
        )
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
                input_hash=input_hash,
            )
        )
        try:
            new_row = (await session.exec(pipeline_stmt)).one()
            await session.commit()
        except UniqueViolationError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Violated unique constraint",
            )

        if config.WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES:
            for value in AnomalyMetricFieldEnum:
                anomaly_detection_rule = AnomalyDetectionRule(
                    pipeline_id=new_row.id,
                    metric_field=value,
                    active=True,
                )
                session.add(anomaly_detection_rule)
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

        # Check if the input data has changed (pipeline code was updated)
        data_changed = row.input_hash != input_hash
        watermark_provided = pipeline.next_watermark is not None

        if data_changed or watermark_provided:
            # Build update values
            update_values = {}

            if data_changed:
                logger.info(
                    f"Pipeline '{pipeline.name}' input data has changed. Updating..."
                )

                # Resolve Pipeline Type Info for update
                pipeline_type_input = PipelineTypePostInput(
                    name=pipeline.pipeline_type_name,
                )
                pipeline_type = PipelineTypePostOutput(
                    **await db_get_or_create_pipeline_type(
                        session=session,
                        pipeline_type=pipeline_type_input,
                        response=response,
                    )
                )

                update_values.update(
                    **new_pipeline.model_dump(exclude={"id"}),
                    pipeline_type_id=pipeline_type.id,
                    input_hash=input_hash,
                    updated_at=pendulum.now("UTC"),
                )

            if watermark_provided:
                logger.info(
                    "Next WaterMark Provided. Updating and Providing WaterMark..."
                )
                update_values["next_watermark"] = pipeline.next_watermark

            # Single update for both data changes and watermark
            update_stmt = (
                update(Pipeline)
                .where(Pipeline.id == pipeline_id)
                .values(**update_values)
            )

            if watermark_provided:
                update_stmt = update_stmt.returning(Pipeline.watermark)
                watermark = (await session.exec(update_stmt)).scalar_one()
            else:
                await session.exec(update_stmt)

            await session.commit()
            logger.info(f"Pipeline '{pipeline.name}' successfully updated")
        else:
            pass  # Input data unchanged, no update needed

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

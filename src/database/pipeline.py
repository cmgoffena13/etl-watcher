import logging
from typing import Optional

import pendulum
from fastapi import HTTPException, Response, status
from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Column, select, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, Session, SQLModel

from src.models.pipeline import PipelinePatchInput

logger = logging.getLogger(__name__)


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(
        index=True, unique=True, nullable=False, max_length=150, min_length=1
    )
    pipeline_type_id: int = Field(foreign_key="pipeline_type.id", nullable=False)
    created_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text(
                "CURRENT_TIMESTAMP"
            ),  # Have Postgres generate the timestamp
        ),
    )
    updated_at: Optional[DateTime] = Field(
        default=None, sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )


async def get_or_create_pipeline(
    session: Session, pipeline: BaseModel, response: Response
) -> dict:
    """Get existing pipeline id or create new one and return id"""
    created = False
    pipeline = Pipeline(**pipeline.model_dump())

    pipeline_id = (
        await session.exec(select(Pipeline.id).where(Pipeline.name == pipeline.name))
    ).scalar_one_or_none()

    if pipeline_id is None:
        logger.info(f"Pipeline '{pipeline.name}' Not Found. Creating...")
        stmt = (
            Pipeline.__table__.insert()
            .returning(Pipeline.__table__.c.id)
            .values(**pipeline.model_dump(exclude={"id"}))
        )
        pipeline_id = (await session.exec(stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(f"Pipeline '{pipeline.name}' Successfully Created")

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": pipeline_id}


async def update_pipeline(session: Session, patch: PipelinePatchInput) -> Pipeline:
    pipeline = (
        await session.exec(select(Pipeline).where(Pipeline.id == patch.id))
    ).scalar_one_or_none()
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found"
        )

    pipeline.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(pipeline, field, value)

    session.add(pipeline)
    await session.commit()
    await session.refresh(pipeline)
    return pipeline

import logging
from enum import Enum
from typing import Optional

import pendulum
from fastapi import HTTPException, Response, status
from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Column, select, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, Session, SQLModel

from src.models.pipeline_type import PipelineTypePatchInput

logger = logging.getLogger(__name__)


class DatePartEnum(str, Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class PipelineType(SQLModel, table=True):
    __tablename__ = "pipeline_type"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(
        index=True, unique=True, nullable=False, max_length=150, min_length=1
    )
    timely_number: Optional[int]
    timely_datepart: Optional[DatePartEnum] = None
    mute_timely_check: bool = Field(default=False)

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
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )


async def get_or_create_pipeline_type(
    session: Session, pipeline_type: BaseModel, response: Response
) -> dict:
    """Get existing pipeline id or create new one and return id"""
    created = False
    pipeline_type = PipelineType(**pipeline_type.model_dump())

    pipeline_type_id = (
        await session.exec(
            select(PipelineType.id).where(PipelineType.name == pipeline_type.name)
        )
    ).scalar_one_or_none()

    if pipeline_type_id is None:
        logger.info(f"Pipeline '{pipeline_type.name}' Not Found. Creating...")
        stmt = (
            PipelineType.__table__.insert()
            .returning(PipelineType.__table__.c.id)
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


async def update_pipeline_type(
    session: Session, patch: PipelineTypePatchInput
) -> PipelineType:
    pipeline_type = (
        await session.exec(select(PipelineType).where(PipelineType.id == patch.id))
    ).scalar_one_or_none()
    if pipeline_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline Type not found"
        )

    pipeline_type.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(pipeline_type, field, value)

    session.add(pipeline_type)
    await session.commit()
    await session.refresh(pipeline_type)
    return pipeline_type

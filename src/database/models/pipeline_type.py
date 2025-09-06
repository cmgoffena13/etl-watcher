from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Boolean, Column, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum


class PipelineType(SQLModel, table=True):
    __tablename__ = "pipeline_type"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(index=True, unique=True, max_length=150, min_length=1)
    timely_number: Optional[int]
    timely_datepart: Optional[DatePartEnum]
    mute_timely_check: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default=text("FALSE"))
    )

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

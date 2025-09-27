from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Boolean, Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum


class PipelineType(SQLModel, table=True):
    __tablename__ = "pipeline_type"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(max_length=150, min_length=1)
    freshness_number: Optional[int]
    freshness_datepart: Optional[DatePartEnum]
    mute_freshness_check: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
    )
    timeliness_number: Optional[int]
    timeliness_datepart: Optional[DatePartEnum]
    mute_timeliness_check: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
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

    __table_args__ = (
        Index(
            "ix_pipeline_type_name_includes",
            "name",
            unique=True,
            postgresql_include=["id"],
        ),
    )

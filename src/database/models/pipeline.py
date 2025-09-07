from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Boolean, Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(nullable=False, max_length=150, min_length=1)
    pipeline_type_id: int = Field(index=True, foreign_key="pipeline_type.id")
    watermark: Optional[str] = Field(max_length=50)
    next_watermark: Optional[str] = Field(max_length=50)

    source_address_id: Optional[int]
    target_address_id: Optional[int]

    pipeline_args: Optional[dict] = Field(sa_column=Column(JSONB))

    last_target_insert: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    last_target_update: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    last_target_soft_delete: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )

    timely_number: Optional[int]
    timely_datepart: Optional[DatePartEnum]
    mute_timely_check: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default=text("FALSE"))
    )

    load_lineage: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default=text("FALSE"))
    )
    active: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default=text("TRUE"))
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
            "ix_pipeline_name_includes",
            "name",
            unique=True,
            postgresql_include=["load_lineage", "active"],
        ),
    )

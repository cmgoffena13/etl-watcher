from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Boolean, Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum, TimelinessDatePartEnum


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_id: int = Field(foreign_key="pipeline_type.id")
    watermark: Optional[str] = Field(max_length=50)
    next_watermark: Optional[str] = Field(max_length=50)

    pipeline_metadata: Optional[dict] = Field(sa_column=Column(JSONB))

    last_target_insert: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    last_target_update: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    last_target_soft_delete: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )

    freshness_number: Optional[int]
    freshness_datepart: Optional[DatePartEnum]
    mute_freshness_check: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
    )
    timeliness_number: Optional[int]
    timeliness_datepart: Optional[TimelinessDatePartEnum]
    mute_timeliness_check: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
    )

    load_lineage: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
    )
    active: bool = Field(
        sa_column=Column(Boolean, server_default=text("TRUE"), nullable=False)
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
            postgresql_include=["load_lineage", "active", "id"],
        ),
        Index(
            "ix_pipeline_pipeline_type_id_includes",
            "pipeline_type_id",
            postgresql_include=["id"],
        ),
    )

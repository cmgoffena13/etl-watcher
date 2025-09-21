from typing import Optional

from pydantic_extra_types.pendulum_dt import Date, DateTime
from sqlalchemy import (
    DECIMAL,
    BigInteger,
    CheckConstraint,
    Column,
    Index,
    Integer,
    text,
)
from sqlalchemy import Date as DateTZ
from sqlalchemy import DateTime as DateTimeTZ
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class PipelineExecution(SQLModel, table=True):
    __tablename__ = "pipeline_execution"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    parent_id: Optional[int]
    pipeline_id: int = Field(foreign_key="pipeline.id")
    start_date: DateTime = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=False)
    )
    date_recorded: Date = Field(sa_column=Column(DateTZ, nullable=False))
    hour_recorded: int = Field(sa_column=Column(Integer, nullable=False))
    end_date: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    duration_seconds: Optional[int]
    completed_successfully: Optional[bool] = None
    inserts: Optional[int] = Field(default=None, ge=0)
    updates: Optional[int] = Field(default=None, ge=0)
    soft_deletes: Optional[int] = Field(default=None, ge=0)
    total_rows: Optional[int] = Field(default=None, ge=0)
    full_load: Optional[bool]
    watermark: Optional[str] = Field(max_length=50)
    next_watermark: Optional[str] = Field(max_length=50)
    execution_metadata: Optional[dict] = Field(sa_column=Column(JSONB, nullable=True))
    throughput: Optional[float] = Field(
        sa_column=Column(
            DECIMAL(precision=12, scale=4), nullable=True
        )  # Up to 10,000,000.0000
    )

    __table_args__ = (
        Index(
            "ix_pipeline_execution_start_date",
            "start_date",
            postgresql_include=["id"],
        ),
        Index(
            "ix_pipeline_execution_hour_recorded",
            "pipeline_id",
            "hour_recorded",
            "end_date",
            postgresql_include=["completed_successfully", "id"],
            postgresql_where=text("end_date IS NOT NULL"),
        ),
        CheckConstraint("end_date IS NULL OR end_date > start_date"),
    )

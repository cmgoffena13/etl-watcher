from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Boolean, Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
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
    end_date: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    duration_seconds: Optional[int]
    completed_successfully: bool = Field(
        sa_column=Column(Boolean, server_default=text("FALSE"), nullable=False)
    )
    inserts: Optional[int] = None
    updates: Optional[int] = None
    soft_deletes: Optional[int] = None
    total_rows: Optional[int] = None
    full_load: Optional[bool]
    watermark: Optional[str] = Field(max_length=50)
    next_watermark: Optional[str] = Field(max_length=50)

    __table_args__ = (
        Index(
            "ix_pipeline_execution_end_date_filter",
            "end_date",
            postgresql_where=text("end_date IS NOT NULL"),
        ),
    )

from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Column
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel


class PipelineExecution(SQLModel, table=True):
    __tablename__ = "pipeline_execution"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    pipeline_id: int = Field(foreign_key="pipeline.id")
    start_date: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
        ),
    )
    end_date: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
    completed_successfully: bool = Field(default=False)
    inserts: Optional[int]
    updates: Optional[int]
    soft_deletes: Optional[int]

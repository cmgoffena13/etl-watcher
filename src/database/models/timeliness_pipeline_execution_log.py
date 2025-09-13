from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Column, ForeignKeyConstraint, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel

from src.types import TimelinessDatePartEnum


class TimelinessPipelineExecutionLog(SQLModel, table=True):
    __tablename__ = "timeliness_pipeline_execution_log"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    pipeline_execution_id: int = Field(sa_column=Column(BigInteger))
    pipeline_id: int = Field(foreign_key="pipeline.id")
    duration_seconds: int
    seconds_threshold: int
    execution_status: str
    timely_number: int
    timely_datepart: TimelinessDatePartEnum
    used_child_config: bool
    created_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text(
                "CURRENT_TIMESTAMP"
            ),  # Have Postgres generate the timestamp
        ),
    )

    __table_args__ = (
        ForeignKeyConstraint(
            columns=["pipeline_execution_id"], refcolumns=["pipeline_execution.id"]
        ),
        Index(
            "ix_timeliness_pipeline_execution_log_execution_id",
            "pipeline_execution_id",
            unique=True,
        ),
    )

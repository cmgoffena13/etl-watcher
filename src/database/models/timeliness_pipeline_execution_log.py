from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Column, ForeignKeyConstraint, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum


class TimelinessPipelineExecutionLog(SQLModel, table=True):
    __tablename__ = "timeliness_pipeline_execution_log"

    pipeline_execution_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    pipeline_id: int = Field(foreign_key="pipeline.id")
    duration_seconds: int
    seconds_threshold: int
    execution_status: str
    timely_number: int
    timely_datepart: DatePartEnum
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
    )

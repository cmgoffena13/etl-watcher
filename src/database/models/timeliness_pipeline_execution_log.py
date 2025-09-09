from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Column, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel


class TimelinessPipelineExecutionLog(SQLModel, table=True):
    __tablename__ = "timeliness_pipeline_execution_log"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    pipeline_execution_id: int = Field(
        foreign_key="pipeline_execution.id", index=True, unique=True
    )
    pipeline_id: int = Field(foreign_key="pipeline.id")
    duration_seconds: int
    seconds_threshold: int
    created_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text(
                "CURRENT_TIMESTAMP"
            ),  # Have Postgres generate the timestamp
        ),
    )

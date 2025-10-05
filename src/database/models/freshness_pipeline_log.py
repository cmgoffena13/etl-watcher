from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BigInteger, Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel

from src.types import DatePartEnum


class FreshnessPipelineLog(SQLModel, table=True):
    __tablename__ = "freshness_pipeline_log"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    pipeline_id: int = Field(foreign_key="pipeline.id")
    last_dml_timestamp: DateTime = Field(sa_column=Column(DateTimeTZ(timezone=True)))
    evaluation_timestamp: DateTime = Field(sa_column=Column(DateTimeTZ(timezone=True)))
    freshness_number: int
    freshness_datepart: DatePartEnum
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
        Index(
            "ux_freshness_pipeline_log",
            "last_dml_timestamp",
            "pipeline_id",
            unique=True,
        ),
    )

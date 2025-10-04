from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Boolean,
    Column,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    text,
)
from sqlalchemy import DateTime as DateTimeTZ
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from src.types import AnomalyMetricFieldEnum


class AnomalyDetectionRule(SQLModel, table=True):
    __tablename__ = "anomaly_detection_rule"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    pipeline_id: int = Field(foreign_key="pipeline.id")
    metric_field: AnomalyMetricFieldEnum = Field(max_length=50)
    z_threshold: float = Field(
        sa_column=Column(DECIMAL(precision=4, scale=2), default=3.0)
    )
    lookback_days: int = Field(default=30)
    minimum_executions: int = Field(default=30)
    active: bool = Field(
        sa_column=Column(Boolean, server_default=text("TRUE"), nullable=False)
    )

    created_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    updated_at: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )

    __table_args__ = (
        Index(
            "ix_anomaly_detection_rule_pipeline_id",
            "pipeline_id",
            "active",
            postgresql_include=["id"],
        ),
        Index(
            "ix_anomaly_detection_rule_composite_key",
            "pipeline_id",
            "metric_field",
            unique=True,
            postgresql_include=["id"],
        ),
    )


class AnomalyDetectionResult(SQLModel, table=True):
    __tablename__ = "anomaly_detection_result"

    pipeline_execution_id: int = Field(sa_column=Column(BigInteger))
    rule_id: int = Field(foreign_key="anomaly_detection_rule.id")

    # Current anomaly values
    violation_value: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))
    z_score: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))

    # Historical baseline statistics
    historical_mean: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))
    std_deviation_value: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))

    # Threshold configuration and values
    z_threshold: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))
    threshold_min_value: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))
    threshold_max_value: float = Field(sa_column=Column(DECIMAL(precision=12, scale=4)))

    context: Optional[dict] = Field(sa_column=Column(JSONB))

    detected_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )

    __table_args__ = (
        PrimaryKeyConstraint("pipeline_execution_id", "rule_id"),
        ForeignKeyConstraint(
            columns=["pipeline_execution_id"], refcolumns=["pipeline_execution.id"]
        ),
    )

from typing import List, Optional

from pydantic import Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.types import AnomalyMetricFieldEnum, ValidatorModel


class AnomalyDetectionRulePostInput(ValidatorModel):
    pipeline_id: int = Field()
    metric_field: AnomalyMetricFieldEnum
    z_threshold: float = Field(
        ge=1.0,
        le=10.0,
        default=2.0,
        description="How many standard deviations above mean to trigger anomaly",
    )
    lookback_days: int = Field(
        ge=1,
        le=365,
        default=30,
        description="Number of days of historical data to compare against",
    )
    minimum_executions: int = Field(
        ge=5,
        le=1000,
        default=10,
        description="Minimum executions needed for baseline calculation",
    )
    active: bool = Field(default=True)


class AnomalyDetectionRulePatchInput(ValidatorModel):
    id: int
    pipeline_id: Optional[int] = None
    metric_field: Optional[AnomalyMetricFieldEnum] = None
    z_threshold: Optional[float] = Field(
        None,
        ge=1.0,
        le=10.0,
        description="How many standard deviations above mean to trigger anomaly",
    )
    lookback_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days of historical data to compare against",
    )
    minimum_executions: Optional[int] = Field(
        None,
        ge=5,
        le=1000,
        description="Minimum executions needed for baseline calculation",
    )
    active: Optional[bool] = None


class AnomalyDetectionRulePostOutput(ValidatorModel):
    id: int


class UnflagAnomalyInput(ValidatorModel):
    pipeline_id: int
    pipeline_execution_id: int
    metric_field: List[AnomalyMetricFieldEnum]


class AnomalyDetectionResultGetOutput(ValidatorModel):
    rule_id: int
    pipeline_execution_id: int

    # Current anomaly values
    violation_value: float
    z_score: float

    # Historical baseline statistics
    historical_mean: float
    std_deviation_value: float

    # Threshold configuration and values
    z_threshold: float
    threshold_min_value: float
    threshold_max_value: float

    context: Optional[dict] = None
    detected_at: DateTime


class AnomalyDetectionSummaryGetOutput(ValidatorModel):
    rule_id: int
    rule_name: str
    anomaly_count: int
    latest_anomaly: Optional[AnomalyDetectionResultGetOutput] = None

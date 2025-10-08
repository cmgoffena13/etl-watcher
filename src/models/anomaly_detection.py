from typing import List, Optional

from pydantic import Field

from src.types import AnomalyMetricFieldEnum, ValidatorModel


class AnomalyDetectionRulePostInput(ValidatorModel):
    pipeline_id: int
    metric_field: AnomalyMetricFieldEnum
    z_threshold: float = Field(
        ge=1.0,
        le=10.0,
        default=3.0,
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
        default=30,
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
    active: Optional[bool] = Field(default=True)


class AnomalyDetectionRulePostOutput(ValidatorModel):
    id: int


class UnflagAnomalyInput(ValidatorModel):
    pipeline_id: int
    pipeline_execution_id: int
    metric_field: List[AnomalyMetricFieldEnum]

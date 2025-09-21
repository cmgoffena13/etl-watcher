from typing import Optional

from pydantic import Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.types import AnomalyMetricFieldEnum, ValidatorModel


class AnomalyDetectionRulePostInput(ValidatorModel):
    pipeline_id: int
    metric_field: AnomalyMetricFieldEnum
    std_deviation_threshold_multiplier: float = Field(ge=1.0, le=10.0, default=2.0)
    lookback_days: int = Field(ge=1, le=365, default=30)
    minimum_executions: int = Field(ge=5, le=1000, default=10)
    active: bool = True


class AnomalyDetectionRulePatchInput(ValidatorModel):
    id: int
    pipeline_id: Optional[int] = None
    metric_field: Optional[AnomalyMetricFieldEnum] = None
    std_deviation_threshold_multiplier: Optional[float] = Field(None, ge=1.0, le=10.0)
    lookback_days: Optional[int] = Field(None, ge=1, le=365)
    minimum_executions: Optional[int] = Field(None, ge=5, le=1000)
    active: Optional[bool] = None


class AnomalyDetectionRulePostOutput(ValidatorModel):
    id: int


# TODO: Implement Summary Endpoint
class AnomalyDetectionResultOutput(ValidatorModel):
    id: int
    rule_id: int
    pipeline_execution_id: int
    metric_value: float
    baseline_value: float
    deviation_percentage: float
    confidence_score: float
    context: Optional[dict] = None
    detected_at: DateTime


class AnomalyDetectionSummary(ValidatorModel):
    rule_id: int
    rule_name: str
    anomaly_count: int
    latest_anomaly: Optional[AnomalyDetectionResultOutput] = None

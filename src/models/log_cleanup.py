from pydantic import Field

from src.types import ValidatorModel


class LogCleanupPostInput(ValidatorModel):
    retention_days: int = Field(ge=90)
    batch_size: int = 10000


class LogCleanupPostOutput(ValidatorModel):
    total_pipeline_executions_deleted: int
    total_timeliness_pipeline_execution_logs_deleted: int
    total_anomaly_detection_results_deleted: int
    total_freshness_pipeline_logs_deleted: int

from pydantic import Field

from src.types import ValidatorModel


class LogCleanupPostInput(ValidatorModel):
    retention_days: int = Field(ge=90)
    batch_size: int = 10000


class LogCleanupPostOutput(ValidatorModel):
    total_pipeline_executions_deleted: int = Field(ge=0)
    total_timeliness_pipeline_execution_logs_deleted: int = Field(ge=0)
    total_anomaly_detection_results_deleted: int = Field(ge=0)
    total_pipeline_execution_closure_parent_deleted: int = Field(ge=0)
    total_pipeline_execution_closure_child_deleted: int = Field(ge=0)
    total_freshness_pipeline_logs_deleted: int = Field(ge=0)

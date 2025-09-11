from typing import Optional

import pendulum
from pydantic import Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.types import ValidatorModel


class PipelineExecutionStartInput(ValidatorModel):
    pipeline_id: int
    start_date: DateTime
    full_load: bool
    watermark: Optional[str] = None
    next_watermark: Optional[str] = None
    parent_id: Optional[int] = None
    execution_metadata: Optional[dict] = None


class PipelineExecutionStartOutput(ValidatorModel):
    id: int


class PipelineExecutionEndInput(ValidatorModel):
    id: int
    pipeline_id: int
    end_date: DateTime
    completed_successfully: bool = Field(default=True)
    inserts: Optional[int] = None
    updates: Optional[int] = None
    soft_deletes: Optional[int] = None
    total_rows: Optional[int] = None

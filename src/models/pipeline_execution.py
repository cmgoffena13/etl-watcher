from typing import Optional

from pydantic import Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.types import LowercaseModel


class PipelineExecutionStartInput(LowercaseModel):
    parent_id: Optional[int] = None
    pipeline_id: int
    start_date: DateTime
    full_load: bool
    watermark: Optional[str] = None
    next_watermark: Optional[str] = None


class PipelineExecutionStartOutput(LowercaseModel):
    id: int


class PipelineExecutionEndInput(LowercaseModel):
    id: int
    end_date: DateTime
    completed_successfully: bool = Field(default=True)
    inserts: Optional[int] = None
    updates: Optional[int] = None
    soft_deletes: Optional[int] = None
    total_rows: Optional[int] = None

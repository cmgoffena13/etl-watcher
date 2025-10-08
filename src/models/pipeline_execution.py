from typing import Optional, Union

from pydantic import Field
from pydantic_extra_types.pendulum_dt import Date, DateTime

from src.types import ValidatorModel


class PipelineExecutionStartInput(ValidatorModel):
    pipeline_id: int
    start_date: DateTime
    watermark: Optional[Union[str, int, DateTime, Date]] = None
    next_watermark: Optional[Union[str, int, DateTime, Date]] = None
    parent_id: Optional[int] = None


class PipelineExecutionStartOutput(ValidatorModel):
    id: int


class PipelineExecutionEndInput(ValidatorModel):
    id: int
    end_date: DateTime
    completed_successfully: bool
    inserts: Optional[int] = Field(default=None, ge=0)
    updates: Optional[int] = Field(default=None, ge=0)
    soft_deletes: Optional[int] = Field(default=None, ge=0)
    total_rows: Optional[int] = Field(default=None, ge=0)
    execution_metadata: Optional[dict] = None

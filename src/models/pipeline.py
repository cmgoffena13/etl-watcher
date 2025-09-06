from typing import Optional, Union

from pydantic import Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.types import DatePartEnum, ValidatorModel


class PipelinePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)
    next_watermark: Optional[Union[str, int, DateTime, None]] = None
    pipeline_args: Optional[dict] = None
    timely_number: Optional[int] = None
    timely_datepart: Optional[DatePartEnum] = None
    mute_timely_check: Optional[bool] = None
    load_lineage: Optional[bool] = None


class PipelinePostOutput(ValidatorModel):
    id: int
    active: bool
    load_lineage: bool
    watermark: Optional[Union[str, int, DateTime, None]] = None


class PipelinePatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    pipeline_type_id: Optional[int] = None

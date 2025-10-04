from typing import Optional, Union

from pydantic import Field
from pydantic_extra_types.pendulum_dt import Date, DateTime

from src.types import DatePartEnum, ValidatorModel


class PipelinePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)
    watermark: Optional[Union[str, int, DateTime, Date]] = None
    next_watermark: Optional[Union[str, int, DateTime, Date]] = None
    pipeline_metadata: Optional[dict] = None
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = False
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None
    mute_timeliness_check: Optional[bool] = False
    load_lineage: Optional[bool] = None


class PipelinePostOutput(ValidatorModel):
    id: int
    active: bool
    load_lineage: bool
    watermark: Optional[Union[str, int, DateTime, Date]] = None


class PipelinePatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    pipeline_type_id: Optional[int] = None
    watermark: Optional[Union[str, int, DateTime, Date]] = None
    next_watermark: Optional[Union[str, int, DateTime, Date]] = None
    pipeline_metadata: Optional[dict] = None
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = None
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None
    mute_timeliness_check: Optional[bool] = None
    load_lineage: Optional[bool] = None

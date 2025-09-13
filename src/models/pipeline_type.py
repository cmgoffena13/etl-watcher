from typing import Optional

from pydantic import Field

from src.types import DatePartEnum, TimelinessDatePartEnum, ValidatorModel


class PipelineTypePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    freshness_number: Optional[int] = None
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = Field(default=False)
    timeliness_number: Optional[int] = None
    timeliness_datepart: Optional[TimelinessDatePartEnum] = None
    mute_timeliness_check: Optional[bool] = Field(default=False)


class PipelineTypePostOutput(ValidatorModel):
    id: int


class PipelineTypePatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    freshness_number: Optional[int] = None
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = None
    timeliness_number: Optional[int] = None
    timeliness_datepart: Optional[TimelinessDatePartEnum] = None
    mute_timeliness_check: Optional[bool] = None

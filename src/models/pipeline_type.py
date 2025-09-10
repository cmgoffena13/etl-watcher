from typing import Optional

from pydantic import Field

from src.types import DatePartEnum, ValidatorModel


class PipelineTypePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    timely_number: Optional[int] = None
    timely_datepart: Optional[DatePartEnum] = None
    mute_timely_check: Optional[bool] = Field(default=False)


class PipelineTypePostOutput(ValidatorModel):
    id: int


class PipelineTypePatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    timely_number: Optional[int] = None
    timely_datepart: Optional[DatePartEnum] = None
    mute_timely_check: Optional[bool] = None

from typing import Optional

from pydantic import BaseModel, Field

from src.database.pipeline_type import DatePartEnum, PipelineType


class PipelineTypePostInput(BaseModel):
    name: str = Field(max_length=150, min_length=1)
    timely_number: Optional[int]
    timely_datepart: Optional[DatePartEnum] = None
    mute_timely_check: Optional[bool] = Field(default=False)


class PipelineTypePostOutput(BaseModel):
    id: int


class PipelineTypePatchInput(BaseModel):
    id: int
    name: Optional[str] = Field(max_length=150, min_length=1)
    timely_number: Optional[int]
    timely_datepart: Optional[DatePartEnum]
    mute_timely_check: Optional[bool]

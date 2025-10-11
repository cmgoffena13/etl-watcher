from typing import Optional, Union

from pydantic import Field, model_validator
from pydantic_extra_types.pendulum_dt import Date, DateTime

from src.types import DatePartEnum, ValidatorModel


class PipelinePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)
    next_watermark: Optional[Union[str, int, DateTime, Date]] = None
    pipeline_metadata: Optional[dict] = None
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None

    @model_validator(mode="after")
    def validate_freshness_fields(self):
        if (self.freshness_number is not None) != (self.freshness_datepart is not None):
            raise ValueError(
                "Both freshness_number and freshness_datepart must be provided together"
            )
        return self

    @model_validator(mode="after")
    def validate_timeliness_fields(self):
        if (self.timeliness_number is not None) != (
            self.timeliness_datepart is not None
        ):
            raise ValueError(
                "Both timeliness_number and timeliness_datepart must be provided together"
            )
        return self


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
    mute_freshness_check: Optional[bool] = Field(default=False)
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None
    mute_timeliness_check: Optional[bool] = Field(default=False)
    load_lineage: Optional[bool] = None
    active: Optional[bool] = Field(default=True)

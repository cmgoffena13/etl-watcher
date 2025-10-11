from typing import Optional

from pydantic import Field, model_validator

from src.types import DatePartEnum, ValidatorModel


class PipelineTypePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = Field(default=False)
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None
    mute_timeliness_check: Optional[bool] = Field(default=False)


class PipelineTypePostOutput(ValidatorModel):
    id: int


class PipelineTypePatchInput(ValidatorModel):
    id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    mute_freshness_check: Optional[bool] = Field(default=False)
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None
    mute_timeliness_check: Optional[bool] = Field(default=False)

    @model_validator(mode="after")
    def validate_id_or_name(self):
        if self.id is None and self.name is None:
            raise ValueError("Either 'id' or 'name' must be provided")
        return self

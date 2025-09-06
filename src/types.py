from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator


class DatePartEnum(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class ValidatorModel(BaseModel):
    @model_validator(mode="before")
    def lowercase_strings(cls, values: dict) -> dict:
        return {
            k: v.lower().strip() if isinstance(v, str) else v for k, v in values.items()
        }

    @model_validator(mode="before")
    def coerce_str_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "next_watermark" in values and values["next_watermark"] is not None:
            values["next_watermark"] = str(values["next_watermark"])
        if "watermark" in values and values["watermark"] is not None:
            values["watermark"] = str(values["watermark"])
        return values

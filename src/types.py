from enum import Enum

from pydantic import BaseModel, model_validator


class DatePartEnum(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class LowercaseModel(BaseModel):
    @model_validator(mode="before")
    def lowercase_strings(cls, values: dict) -> dict:
        return {
            k: v.lower().strip() if isinstance(v, str) else v for k, v in values.items()
        }

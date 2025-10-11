from enum import Enum
from typing import Any

import orjson
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator


class DatePartEnum(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AnomalyMetricFieldEnum(str, Enum):
    DURATION_SECONDS = "duration_seconds"
    INSERTS = "inserts"
    UPDATES = "updates"
    SOFT_DELETES = "soft_deletes"
    TOTAL_ROWS = "total_rows"
    THROUGHPUT = "throughput"


class ValidatorModel(BaseModel):
    @model_validator(mode="before")
    def lowercase_strings(cls, values: dict) -> dict:
        # Ordering prevents this, but just in case
        preserve_case_fields = {
            "watermark",
            "next_watermark",
        }

        return {
            k: v.lower().strip()
            if isinstance(v, str) and k not in preserve_case_fields
            else v
            for k, v in values.items()
        }

    @model_validator(mode="before")
    def coerce_str_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "next_watermark" in values and values["next_watermark"] is not None:
            values["next_watermark"] = str(values["next_watermark"])
        if "watermark" in values and values["watermark"] is not None:
            values["watermark"] = str(values["watermark"])
        return values


class ORJSONResponse(JSONResponse):
    """
    Function to convert JSON directly to bytes.
    Faster Serialization than default.
    Requester needs to use orjson to decode.
    """

    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content)

from enum import Enum

import httpx
import pendulum
from pydantic import BaseModel, Field, Optional, Union
from pydantic_extra_types.pendulum_dt import Date, DateTime


class DatePartEnum(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Pipeline(BaseModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)
    next_watermark: Optional[Union[str, int, DateTime, Date]] = None
    freshness_number: Optional[int] = Field(default=None, gt=0)
    freshness_datepart: Optional[DatePartEnum] = None
    timeliness_number: Optional[int] = Field(default=None, gt=0)
    timeliness_datepart: Optional[DatePartEnum] = None


class PipelineResponse(BaseModel):
    id: int
    watermark: Optional[Union[str, int, DateTime, Date]] = None
    active: bool
    load_lineage: bool


class ETLMetrics(BaseModel):
    completed_successfully: bool
    inserts: Optional[int] = Field(..., ge=0)
    updates: Optional[int] = Field(..., ge=0)
    soft_deletes: Optional[int] = Field(..., ge=0)
    total_rows: Optional[int] = Field(..., ge=0)
    execution_metadata: Optional[dict] = None


class EndProcessExecutionInput(ETLMetrics):
    id: int
    end_date: str = Field(default=pendulum.now("UTC").isoformat())


base_url = "http://localhost:8000"


def track_pipeline_execution(
    pipeline_id: int, parent_execution_id: Optional[int] = None
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_execution = {
                "pipeline_id": pipeline_id,
                "start_date": pendulum.now("UTC").isoformat(),
            }
            if parent_execution_id is not None:
                start_execution["parent_id"] = parent_execution_id
            start_response = httpx.post(
                f"{base_url}/start_pipeline_execution", json=start_execution
            )
            execution_id = start_response.json()["id"]

            try:
                result = func(*args, **kwargs)
                end_process_execution_input = EndProcessExecutionInput(
                    id=execution_id, **result.model_dump()
                )

                httpx.post(
                    f"{base_url}/end_pipeline_execution",
                    json={end_process_execution_input.model_dump()},
                )

                return result

            except Exception as e:
                result_metrics = ETLMetrics(
                    id=execution_id, completed_successfully=False
                )
                httpx.post(
                    f"{base_url}/end_pipeline_execution",
                    json={result_metrics.model_dump()},
                )
                raise e

        return wrapper

    return decorator


def sync_pipeline(pipeline_config: dict, next_watermark: Optional[str] = None):
    if next_watermark is not None:
        pipeline_config["pipeline"].next_watermark = next_watermark
    response = httpx.post(f"{base_url}/pipeline", json=pipeline_config["pipeline"])
    pipeline_response = PipelineResponse(**response.json())
    if pipeline_response.load_lineage:
        pipeline_config["lineage"]["pipeline_id"] = pipeline_response.id
        httpx.post(f"{base_url}/address_lineage", json=pipeline_config["lineage"])
    if pipeline_response.watermark is None:
        pipeline_config["watermark"] = pipeline_config["default_watermark"]
    else:
        # Assumes watermark will always be a date. Need to adjust.
        pipeline_config["watermark"] = pendulum.parse(
            pipeline_response.watermark
        ).date()
    return pipeline_response

from typing import Optional

from pydantic import Field

from src.types import LowercaseModel


class PipelinePostInput(LowercaseModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)


class PipelinePostOutput(LowercaseModel):
    id: int


class PipelinePatchInput(LowercaseModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    pipeline_type_id: Optional[int] = None

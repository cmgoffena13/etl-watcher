from typing import Optional

from pydantic import BaseModel, Field


class PipelinePostInput(BaseModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)


class PipelinePatchInput(BaseModel):
    id: int
    name: Optional[str] = Field(max_length=150, min_length=1)


class PipelinePostOutput(BaseModel):
    id: int


class PipelineIDGetInput(BaseModel):
    name: str = Field(max_length=150, min_length=1)
    pipeline_type_name: str = Field(max_length=150, min_length=1)


class PipelineIDGetOutput(BaseModel):
    id: int

from typing import List, Optional, Union

from pydantic import Field

from src.types import ValidatorModel


class SourceAddress(ValidatorModel):
    address_name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)


class TargetAddress(ValidatorModel):
    address_name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)

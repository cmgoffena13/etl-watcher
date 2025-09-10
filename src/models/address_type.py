from typing import Optional

from pydantic import Field

from src.types import ValidatorModel


class AddressTypePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    group_name: str = Field(max_length=150, min_length=1)


class AddressTypePostOutput(ValidatorModel):
    id: int


class AddressTypePatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    group_name: Optional[str] = Field(None, max_length=150, min_length=1)

from typing import Optional

from pydantic import Field, model_validator

from src.types import ValidatorModel


class AddressTypePostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    group_name: str = Field(max_length=150, min_length=1)


class AddressTypePostOutput(ValidatorModel):
    id: int


class AddressTypePatchInput(ValidatorModel):
    id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    group_name: Optional[str] = Field(None, max_length=150, min_length=1)

    @model_validator(mode="after")
    def validate_id_or_name(self):
        if self.id is None and self.name is None:
            raise ValueError("Either 'id' or 'name' must be provided")
        return self

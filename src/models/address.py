from typing import Optional

from pydantic import Field, model_validator

from src.types import ValidatorModel


class AddressPostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)
    address_type_group_name: str = Field(max_length=150, min_length=1)
    database_name: Optional[str] = Field(None, max_length=50)
    schema_name: Optional[str] = Field(None, max_length=50)
    table_name: Optional[str] = Field(None, max_length=50)
    primary_key: Optional[str] = Field(None, max_length=50)
    address_metadata: Optional[dict] = None


class AddressPostOutput(ValidatorModel):
    id: int


class AddressPatchInput(ValidatorModel):
    id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    address_type_id: Optional[int] = None
    database_name: Optional[str] = Field(None, max_length=50)
    schema_name: Optional[str] = Field(None, max_length=50)
    table_name: Optional[str] = Field(None, max_length=50)
    primary_key: Optional[str] = Field(None, max_length=50)

    @model_validator(mode="after")
    def validate_id_or_name(self):
        if self.id is None and self.name is None:
            raise ValueError("Either 'id' or 'name' must be provided")
        return self

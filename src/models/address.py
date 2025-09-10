from typing import Optional

from pydantic import Field

from src.types import ValidatorModel


class AddressPostInput(ValidatorModel):
    name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)
    address_type_group_name: str = Field(max_length=150, min_length=1)
    database_name: Optional[str] = Field(None, max_length=50)
    schema_name: Optional[str] = Field(None, max_length=50)
    table_name: Optional[str] = Field(None, max_length=50)
    primary_key: Optional[str] = Field(None, max_length=50)
    deprecated: Optional[bool] = False


class AddressPostOutput(ValidatorModel):
    id: int


class AddressPatchInput(ValidatorModel):
    id: int
    name: Optional[str] = Field(None, max_length=150, min_length=1)
    address_type_id: Optional[int] = None
    database_name: Optional[str] = Field(None, max_length=50)
    schema_name: Optional[str] = Field(None, max_length=50)
    table_name: Optional[str] = Field(None, max_length=50)
    primary_key: Optional[str] = Field(None, max_length=50)
    deprecated: Optional[bool] = False
    address_type_id: Optional[int] = None

from typing import List

from pydantic import Field

from src.types import ValidatorModel


class SourceAddress(ValidatorModel):
    address_name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)


class TargetAddress(ValidatorModel):
    address_name: str = Field(max_length=150, min_length=1)
    address_type_name: str = Field(max_length=150, min_length=1)


class AddressLineagePostInput(ValidatorModel):
    pipeline_id: int
    source_addresses: List[SourceAddress]
    target_addresses: List[TargetAddress]


class AddressLineagePostOutput(ValidatorModel):
    pipeline_id: int
    lineage_relationships_created: int


class AddressLineageGetOutput(ValidatorModel):
    id: int
    pipeline_id: int
    source_address_id: int
    target_address_id: int

from typing import List, Optional

from src.models.address import AddressPostInput
from src.types import ValidatorModel


class AddressLineagePostInput(ValidatorModel):
    pipeline_id: int
    source_addresses: List[AddressPostInput]
    target_addresses: List[AddressPostInput]


class AddressLineagePostOutput(ValidatorModel):
    pipeline_id: int
    lineage_relationships_created: int
    message: Optional[str] = None


class AddressLineageGetOutput(ValidatorModel):
    id: int
    pipeline_id: int
    source_address_id: int
    target_address_id: int


class AddressLineageClosureGetOutput(ValidatorModel):
    source_address_id: int
    target_address_id: int
    depth: int
    source_address_name: str
    target_address_name: str

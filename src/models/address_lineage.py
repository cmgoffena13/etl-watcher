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

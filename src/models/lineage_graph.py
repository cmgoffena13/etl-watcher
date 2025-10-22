from typing import Optional

from src.types import ValidatorModel


class LineageGraphNode(ValidatorModel):
    """Node in the lineage graph representing an address."""

    id: int
    name: str
    address_type_name: str
    address_type_group_name: str
    address_metadata: Optional[dict] = None


class LineageGraphEdge(ValidatorModel):
    """Edge in the lineage graph representing a relationship."""

    source_address_id: int
    target_address_id: int
    depth: int
    lineage_path: list[int]
    pipeline_id: Optional[int] = None
    pipeline_name: Optional[str] = None
    pipeline_type_name: Optional[str] = None
    pipeline_metadata: Optional[dict] = None
    pipeline_active: Optional[bool] = None


class LineageGraphResponse(ValidatorModel):
    """Complete lineage graph response."""

    nodes: list[LineageGraphNode]
    edges: list[LineageGraphEdge]

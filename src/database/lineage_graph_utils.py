import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lineage_graph import (
    LineageGraphEdge,
    LineageGraphNode,
    LineageGraphResponse,
)

logger = logging.getLogger(__name__)


async def db_get_lineage_graph(
    session: AsyncSession,
    source_address_id: Optional[int] = None,
    target_address_id: Optional[int] = None,
    depth: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    pipeline_type_name: Optional[str] = None,
    pipeline_active: Optional[bool] = None,
) -> LineageGraphResponse:
    """Get lineage graph data from materialized view."""

    # Build WHERE clause based on filters
    where_conditions = []
    params = {}

    if source_address_id is not None:
        where_conditions.append("source_address_id = :source_address_id")
        params["source_address_id"] = source_address_id

    if target_address_id is not None:
        where_conditions.append("target_address_id = :target_address_id")
        params["target_address_id"] = target_address_id

    if depth is not None:
        where_conditions.append("depth = :depth")
        params["depth"] = depth

    if pipeline_id is not None:
        where_conditions.append("pipeline_id = :pipeline_id")
        params["pipeline_id"] = pipeline_id

    if pipeline_type_name is not None:
        where_conditions.append("pipeline_type_name = :pipeline_type_name")
        params["pipeline_type_name"] = pipeline_type_name

    if pipeline_active is not None:
        where_conditions.append("pipeline_active = :pipeline_active")
        params["pipeline_active"] = pipeline_active

    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
    SELECT 
        source_address_id,
        target_address_id,
        depth,
        lineage_path,
        source_address_name,
        source_address_type_name,
        source_address_group_name,
        source_address_metadata,
        target_address_name,
        target_address_type_name,
        target_address_group_name,
        target_address_metadata,
        pipeline_id,
        pipeline_name,
        pipeline_type_name,
        pipeline_metadata,
        pipeline_active
    FROM lineage_graph_report
    {where_clause}
    ORDER BY source_address_id, target_address_id, depth
    """

    try:
        logger.info(f"Executing query: {query}")
        logger.info(f"With params: {params}")
        rows = (await session.exec(text(query), params=params)).fetchall()
        logger.info(f"Query returned {len(rows)} rows")

        # Build nodes and edges
        nodes = {}
        edges = []

        for row in rows:
            # Add source address node
            if row.source_address_id not in nodes:
                nodes[row.source_address_id] = LineageGraphNode(
                    id=row.source_address_id,
                    name=row.source_address_name,
                    address_type_name=row.source_address_type_name,
                    address_type_group_name=row.source_address_group_name,
                    address_metadata=row.source_address_metadata,
                )

            # Add target address node
            if row.target_address_id not in nodes:
                nodes[row.target_address_id] = LineageGraphNode(
                    id=row.target_address_id,
                    name=row.target_address_name,
                    address_type_name=row.target_address_type_name,
                    address_type_group_name=row.target_address_group_name,
                    address_metadata=row.target_address_metadata,
                )

            # Add edge with pipeline info
            edge = LineageGraphEdge(
                source_address_id=row.source_address_id,
                target_address_id=row.target_address_id,
                depth=row.depth,
                lineage_path=row.lineage_path,
                pipeline_id=row.pipeline_id,
                pipeline_name=row.pipeline_name,
                pipeline_type_name=row.pipeline_type_name,
                pipeline_metadata=row.pipeline_metadata,
                pipeline_active=row.pipeline_active,
            )
            edges.append(edge)

        return LineageGraphResponse(nodes=list(nodes.values()), edges=edges)

    except Exception as e:
        logger.error(f"Error getting lineage graph: {e}")
        raise

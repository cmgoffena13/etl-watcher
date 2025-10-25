import logging

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
    source_address_id: int,
) -> LineageGraphResponse:
    """Get lineage graph data from materialized view."""

    query = """
    WITH all_address_ids AS (
        SELECT target_address_id as address_id
        FROM lineage_graph_report 
        WHERE source_address_id = :source_address_id
        UNION ALL
        SELECT :source_address_id as address_id
        UNION ALL
        SELECT source_address_id as address_id
        FROM lineage_graph_report
        WHERE target_address_id = :source_address_id
    )
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
    WHERE lineage_path && (SELECT ARRAY_AGG(address_id) FROM all_address_ids)
        AND depth = 1
    """
    params = {"source_address_id": source_address_id}

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

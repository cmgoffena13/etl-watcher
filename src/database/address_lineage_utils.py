import logging
import time
from typing import List, Set

from fastapi import Response
from sqlalchemy import select
from sqlmodel import Session

from src.database.address_utils import db_get_or_create_address
from src.database.models.address_lineage import AddressLineage
from src.database.models.address_lineage_closure import AddressLineageClosure
from src.models.address import AddressPostInput, AddressPostOutput
from src.models.address_lineage import (
    AddressLineagePostInput,
    AddressLineagePostOutput,
    SourceAddress,
    TargetAddress,
)

logger = logging.getLogger(__name__)


async def _process_address_lists(
    session: Session,
    source_addresses: List[SourceAddress],
    target_addresses: List[TargetAddress],
    response: Response,
) -> tuple[Set[int], Set[int]]:
    source_address_ids = set()
    target_address_ids = set()

    # Process source addresses
    for source_address in source_addresses:
        source_address_input = AddressPostInput(
            name=source_address.address_name,
            address_type_name=source_address.address_type_name,
        )
        source_address = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=source_address_input, response=response
            )
        )
        source_address_ids.add(source_address.id)

    # Process target addresses
    for target_address in target_addresses:
        target_address_input = AddressPostInput(
            name=target_address.address_name,
            address_type_name=target_address.address_type_name,
        )
        target_address = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=target_address_input, response=response
            )
        )
        target_address_ids.add(target_address.id)

    return source_address_ids, target_address_ids


async def _create_address_lineage_relationships(
    session: Session,
    pipeline_id: int,
    source_address_ids: Set[int],
    target_address_ids: Set[int],
) -> int:
    logger.info(
        f"Creating {len(source_address_ids)} x {len(target_address_ids)} = {len(source_address_ids) * len(target_address_ids)} lineage relationships for pipeline {pipeline_id}"
    )

    # Create lineage records
    lineage_relationships = []
    for source_address_id in source_address_ids:
        for target_address_id in target_address_ids:
            lineage_relationships.append(
                {
                    "pipeline_id": pipeline_id,
                    "source_address_id": source_address_id,
                    "target_address_id": target_address_id,
                }
            )

    # Delete + Insert to ensure lineage is always accurate
    savepoint = await session.begin_nested()
    try:
        await session.exec(
            AddressLineage.__table__.delete().where(
                AddressLineage.pipeline_id == pipeline_id
            )
        )
        await session.exec(
            AddressLineage.__table__.insert().values(lineage_relationships)
        )

        # Closer Table Rebuild gets its own savepoint/transaction to ensure atomicity
        await savepoint.commit()
        await session.commit()

        # Rebuild closure table after lineage changes
        affected_address_ids = source_address_ids.union(target_address_ids)
        await _rebuild_closure_table_incremental(
            session, affected_address_ids, pipeline_id
        )
    except Exception:
        await savepoint.rollback()
        raise
    return len(lineage_relationships)


async def db_create_address_lineage(
    session: Session, lineage_input: AddressLineagePostInput, response: Response
) -> AddressLineagePostOutput:
    source_address_ids, target_address_ids = await _process_address_lists(
        session,
        lineage_input.source_addresses,
        lineage_input.target_addresses,
        response,
    )

    relationships_created = await _create_address_lineage_relationships(
        session, lineage_input.pipeline_id, source_address_ids, target_address_ids
    )

    return {
        "pipeline_id": lineage_input.pipeline_id,
        "lineage_relationships_created": relationships_created,
    }


async def db_get_address_lineage_by_pipeline(
    session: Session, pipeline_id: int
) -> List[AddressLineage]:
    return (
        (
            await session.exec(
                select(AddressLineage).where(AddressLineage.pipeline_id == pipeline_id)
            )
        )
        .scalars()
        .all()
    )


async def _rebuild_closure_table_incremental(
    session: Session, connected_addresses: Set[int], pipeline_id: int
) -> None:
    logger.info(f"Rebuilding closure table for {len(connected_addresses)} addresses")

    savepoint = await session.begin_nested()
    try:
        # Traverse to find all connected addresses and collect edges simultaneously
        start_time = time.time()
        all_edges = set()
        added = True
        while added:
            added = False

            # Get new addresses where source is in connected_addresses
            forward_edges = (
                await session.exec(
                    select(
                        AddressLineage.source_address_id,
                        AddressLineage.target_address_id,
                    ).where(AddressLineage.source_address_id.in_(connected_addresses))
                )
            ).all()

            # Get new addresses where target is in connected_addresses
            backward_edges = (
                await session.exec(
                    select(
                        AddressLineage.source_address_id,
                        AddressLineage.target_address_id,
                    ).where(AddressLineage.target_address_id.in_(connected_addresses))
                )
            ).all()

            # Collect edges for closure building
            all_edges.update(forward_edges)
            all_edges.update(backward_edges)

            # Add new connected addresses from forward traversal
            for edge in forward_edges:
                if edge.target_address_id not in connected_addresses:
                    connected_addresses.add(edge.target_address_id)
                    added = True

            # Add new connected addresses from backward traversal
            for edge in backward_edges:
                if edge.source_address_id not in connected_addresses:
                    connected_addresses.add(edge.source_address_id)
                    added = True

        # Log edge collection timing
        edge_collection_time = time.time() - start_time
        logger.info(
            f"Edge collection completed for pipeline {pipeline_id}:"
            f"\n{len(connected_addresses)} addresses, {len(all_edges)} edges in {edge_collection_time:.3f}s"
        )

        # Delete all closure paths that involve any of the connected addresses
        # Use two separate deletes to leverage indexes efficiently
        await session.exec(
            AddressLineageClosure.__table__.delete().where(
                AddressLineageClosure.source_address_id.in_(connected_addresses)
            )
        )
        await session.exec(
            AddressLineageClosure.__table__.delete().where(
                AddressLineageClosure.target_address_id.in_(connected_addresses)
            )
        )

        closure_start_time = time.time()
        closure = set()

        # Add self-references (depth 0)
        for n in connected_addresses:
            closure.add((n, n, 0))

        # Propagate paths
        added = True
        while added:
            added = False

            new_paths = set()
            # Loop through Depth 0
            for initial_source, initial_target, initial_depth in closure:
                # Now Loop through all edges
                for edge_source, edge_target in all_edges:
                    # If the edge source is the target of a Depth 0 record, extend the lineage
                    if edge_source == initial_target:
                        candidate = (initial_source, edge_target, initial_depth + 1)
                        if candidate not in closure:
                            new_paths.add(candidate)
                            added = True

            closure.update(new_paths)

        # Log closure algorithm timing
        closure_time = time.time() - closure_start_time
        logger.info(
            f"Closure algorithm completed for {pipeline_id}:"
            f"\n{len(closure)} paths in {closure_time:.3f}s"
        )

        closure_records = [
            {
                "source_address_id": source_address_id,
                "target_address_id": target_address_id,
                "depth": depth,
            }
            for source_address_id, target_address_id, depth in closure
        ]

        await session.exec(
            AddressLineageClosure.__table__.insert().values(closure_records)
        )

        await savepoint.commit()
        await session.commit()
    except Exception:
        await savepoint.rollback()
        raise

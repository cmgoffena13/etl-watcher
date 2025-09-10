import logging
import time
from typing import List, Set, Tuple

from fastapi import Response
from sqlalchemy import alias, desc, literal_column, select, union_all
from sqlmodel import Session

from src.database.address_utils import db_get_or_create_address
from src.database.models.address import Address
from src.database.models.address_lineage import AddressLineage
from src.database.models.address_lineage_closure import AddressLineageClosure
from src.database.models.pipeline import Pipeline
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
            address_type_group_name=source_address.address_type_group_name,
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
            address_type_group_name=target_address.address_type_group_name,
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
        delete_result = await session.exec(
            AddressLineage.__table__.delete().where(
                AddressLineage.pipeline_id == pipeline_id
            )
        )
        insert_result = await session.exec(
            AddressLineage.__table__.insert().values(lineage_relationships)
        )

        logger.info(
            f"Lineage operations for pipeline {pipeline_id}: deleted {delete_result.rowcount} existing records, inserted {insert_result.rowcount} new records"
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
    pipeline = await session.get(Pipeline, lineage_input.pipeline_id)
    if not pipeline or not pipeline.load_lineage:
        response.status_code = 200
        return {
            "pipeline_id": lineage_input.pipeline_id,
            "lineage_relationships_created": 0,
            "message": f"Pipeline {lineage_input.pipeline_id} does not have load_lineage=True. No lineage relationships created.",
        }

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
        "message": f"Lineage relationships created for pipeline {lineage_input.pipeline_id}",
    }


async def db_get_address_lineage_for_address(
    session: Session, address_id: int
) -> List[Tuple[int, int, int, str, str]]:
    """
    Get lineage for a specific address using the closure table.
    Returns all relationships where the address is either source or target.
    """

    # Create aliases for the Address table
    SourceAddress = alias(Address)
    TargetAddress = alias(Address)

    # Query for relationships where address is the source
    downstream_query = (
        select(
            AddressLineageClosure.source_address_id,
            AddressLineageClosure.target_address_id,
            AddressLineageClosure.depth,
            SourceAddress.c.name.label("source_address_name"),
            TargetAddress.c.name.label("target_address_name"),
        )
        .join(
            SourceAddress, AddressLineageClosure.source_address_id == SourceAddress.c.id
        )
        .join(
            TargetAddress, AddressLineageClosure.target_address_id == TargetAddress.c.id
        )
        .where(AddressLineageClosure.source_address_id == address_id)
        .where(AddressLineageClosure.depth > 0)
    )

    # Query for relationships where address is the target
    upstream_query = (
        select(
            AddressLineageClosure.source_address_id,
            AddressLineageClosure.target_address_id,
            AddressLineageClosure.depth,
            SourceAddress.c.name.label("source_address_name"),
            TargetAddress.c.name.label("target_address_name"),
        )
        .join(
            SourceAddress, AddressLineageClosure.source_address_id == SourceAddress.c.id
        )
        .join(
            TargetAddress, AddressLineageClosure.target_address_id == TargetAddress.c.id
        )
        .where(AddressLineageClosure.target_address_id == address_id)
        .where(AddressLineageClosure.depth > 0)
    )

    # Union the two queries and order by depth
    union_query = union_all(downstream_query, upstream_query).order_by(desc("depth"))

    result = await session.exec(union_query)
    return result.fetchall()


async def _rebuild_closure_table_incremental(
    session: Session, connected_addresses: Set[int], pipeline_id: int
) -> None:
    logger.info(
        f"Rebuilding closure table for {len(connected_addresses)} addresses for pipeline {pipeline_id}"
    )

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
            f"Edge collection completed for pipeline {pipeline_id}: {len(connected_addresses)} addresses, {len(all_edges)} edges in {edge_collection_time:.3f}s"
        )

        # Delete all closure paths that involve any of the connected addresses
        # Use two separate deletes to leverage indexes efficiently
        delete_result_1 = await session.exec(
            AddressLineageClosure.__table__.delete().where(
                AddressLineageClosure.source_address_id.in_(connected_addresses)
            )
        )
        delete_result_2 = await session.exec(
            AddressLineageClosure.__table__.delete().where(
                AddressLineageClosure.target_address_id.in_(connected_addresses)
            )
        )

        total_deleted = delete_result_1.rowcount + delete_result_2.rowcount
        logger.info(
            f"Deleted {total_deleted} closure records (source: {delete_result_1.rowcount}, target: {delete_result_2.rowcount}) for pipeline {pipeline_id}"
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
            f"Closure algorithm completed for pipeline {pipeline_id}: {len(closure)} paths in {closure_time:.3f}s"
        )

        closure_records = [
            {
                "source_address_id": source_address_id,
                "target_address_id": target_address_id,
                "depth": depth,
            }
            for source_address_id, target_address_id, depth in closure
        ]

        insert_result = await session.exec(
            AddressLineageClosure.__table__.insert().values(closure_records)
        )
        logger.info(
            f"Inserted {insert_result.rowcount} closure records for pipeline {pipeline_id}"
        )

        await savepoint.commit()
        await session.commit()
    except Exception:
        await savepoint.rollback()
        raise

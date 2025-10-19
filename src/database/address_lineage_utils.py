import logging
import time
from typing import List, Set, Tuple

from fastapi import Response
from sqlalchemy import alias, desc, select, union_all
from sqlmodel import Session

from src.database.address_utils import db_get_or_create_address
from src.database.models.address import Address
from src.database.models.address_lineage import AddressLineage, AddressLineageClosure
from src.database.models.pipeline import Pipeline
from src.models.address import AddressPostInput, AddressPostOutput
from src.models.address_lineage import (
    AddressLineagePostInput,
    AddressLineagePostOutput,
)

logger = logging.getLogger(__name__)


async def _process_address_lists(
    session: Session,
    source_addresses: List[AddressPostInput],
    target_addresses: List[AddressPostInput],
    response: Response,
) -> tuple[Set[int], Set[int]]:
    source_address_ids = set()
    target_address_ids = set()

    # Process source addresses
    for source_address in source_addresses:
        source_address_output = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=source_address, response=response
            )
        )
        source_address_ids.add(source_address_output.id)

    # Process target addresses
    for target_address in target_addresses:
        target_address_output = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=target_address, response=response
            )
        )
        target_address_ids.add(target_address_output.id)

    return source_address_ids, target_address_ids


async def _create_address_lineage_relationships(
    session: Session,
    pipeline_id: int,
    source_address_ids: Set[int],
    target_address_ids: Set[int],
) -> tuple[int, Set[int], int]:
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

        await savepoint.commit()
        await session.commit()
    except Exception:
        await savepoint.rollback()
        raise

    # Return relationships count, affected address IDs, and pipeline ID for background processing
    affected_address_ids = source_address_ids.union(target_address_ids)
    return len(lineage_relationships), affected_address_ids, pipeline_id


async def db_create_address_lineage(
    session: Session, lineage_input: AddressLineagePostInput, response: Response
) -> tuple[AddressLineagePostOutput, Set[int], int]:
    pipeline = await session.get(Pipeline, lineage_input.pipeline_id)
    if not pipeline or not pipeline.load_lineage:
        response.status_code = 200
        return (
            {
                "pipeline_id": lineage_input.pipeline_id,
                "lineage_relationships_created": 0,
                "message": f"Pipeline {lineage_input.pipeline_id} does not have load_lineage=True. No lineage relationships created.",
            },
            set(),
            lineage_input.pipeline_id,
        )

    source_address_ids, target_address_ids = await _process_address_lists(
        session,
        lineage_input.source_addresses,
        lineage_input.target_addresses,
        response,
    )

    (
        relationships_created,
        affected_address_ids,
        pipeline_id,
    ) = await _create_address_lineage_relationships(
        session, lineage_input.pipeline_id, source_address_ids, target_address_ids
    )

    return (
        {
            "pipeline_id": lineage_input.pipeline_id,
            "lineage_relationships_created": relationships_created,
            "message": f"Lineage relationships created for pipeline {lineage_input.pipeline_id}",
        },
        affected_address_ids,
        pipeline_id,
    )


async def db_rebuild_closure_table_incremental(
    session: Session, connected_addresses: Set[int], pipeline_id: int
) -> None:
    logger.info(
        f"Rebuilding closure table for {len(connected_addresses)} addresses for pipeline {pipeline_id}"
    )
    try:
        # Traverse to find all connected addresses and collect edges simultaneously
        start_time = time.time()
        all_edges = set()
        added = True
        while added:
            added = False

            # Get new addresses where source is in connected_addresses - downstream edges
            forward_edges = (
                await session.exec(
                    select(
                        AddressLineage.source_address_id,
                        AddressLineage.target_address_id,
                    ).where(AddressLineage.source_address_id.in_(connected_addresses))
                )
            ).all()

            # Get new addresses where target is in connected_addresses - upstream edges
            backward_edges = (
                await session.exec(
                    select(
                        AddressLineage.source_address_id,
                        AddressLineage.target_address_id,
                    ).where(AddressLineage.target_address_id.in_(connected_addresses))
                )
            ).all()

            all_edges.update(forward_edges)
            all_edges.update(backward_edges)

            # Add new connected addresses from forward traversal - downstream addresses
            for source_address, target_address in forward_edges:
                if target_address not in connected_addresses:
                    connected_addresses.add(target_address)
                    added = True

            # Add new connected addresses from backward traversal - upstream addresses
            for source_address, target_address in backward_edges:
                if source_address not in connected_addresses:
                    connected_addresses.add(source_address)
                    added = True

        # Log edge collection timing
        edge_collection_time = time.time() - start_time
        logger.info(
            f"Edge collection completed for pipeline {pipeline_id}: {len(connected_addresses)} addresses, {len(all_edges)} edges in {edge_collection_time:.3f}s"
        )

        savepoint = await session.begin_nested()
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
        # Holds records for insertion into the closure table
        closure = set()

        # Add self-references (depth 0) - using tuple for hashability
        for n in connected_addresses:
            closure.add((n, n, 0, tuple([n])))

        # Add direct relationships (depth 1) - using tuples for hashability
        for source_address, target_address in all_edges:
            closure.add(
                (
                    source_address,
                    target_address,
                    1,
                    tuple([source_address, target_address]),
                )
            )

        # Propagate paths - extend from existing paths
        added = True
        while added:
            added = False
            new_transitive_paths = set()

            # Loop through existing paths in closure
            for (
                existing_source_address,
                existing_target_address,
                existing_depth,
                existing_lineage_path,
            ) in closure:
                # Skip self-references
                if existing_depth == 0:
                    continue
                # Now Loop through all edges
                for source_address, target_address in all_edges:
                    # If a source address is the target address of an existing path, extend the lineage with the transitive path
                    if source_address == existing_target_address:
                        new_target_address = target_address
                        new_depth = existing_depth + 1
                        new_lineage_path = tuple(
                            list(existing_lineage_path) + [target_address]
                        )
                        candidate = (
                            existing_source_address,
                            new_target_address,
                            new_depth,
                            new_lineage_path,
                        )

                        if candidate not in closure:
                            new_transitive_paths.add(candidate)
                            added = True

            closure.update(new_transitive_paths)

        # Log closure algorithm timing
        closure_time = time.time() - closure_start_time
        logger.info(
            f"Closure algorithm completed for pipeline {pipeline_id}: {len(closure)} paths in {closure_time:.3f}s"
        )

        closure_records = [
            AddressLineageClosure(
                source_address_id=source_address_id,
                target_address_id=target_address_id,
                depth=depth,
                lineage_path=list(
                    lineage_path
                ),  # Convert tuple back to list for array storage
            )
            for source_address_id, target_address_id, depth, lineage_path in closure
        ]

        session.add_all(closure_records)

        await savepoint.commit()
        await session.commit()
        logger.info(
            f"Inserted {len(closure_records)} closure records for pipeline {pipeline_id}"
        )
    except Exception:
        await savepoint.rollback()
        raise

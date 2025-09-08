import logging
from typing import List, Set

from fastapi import Response
from sqlalchemy import select
from sqlmodel import Session

from src.database.address_utils import db_get_or_create_address
from src.database.models.address_lineage import AddressLineage
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
        await savepoint.commit()
        await session.commit()
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

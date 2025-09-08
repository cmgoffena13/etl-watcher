import logging

from fastapi import Response, status
from sqlalchemy import select
from sqlmodel import Session

from src.database.models.address_lineage import AddressLineage
from src.models.address import AddressPostInput, AddressPostOutput
from src.models.address_type import AddressTypePostInput, AddressTypePostOutput

logger = logging.getLogger(__name__)


async def _create_address_lineage_relationships(
    session: Session,
    pipeline_id: int,
    source_address_ids: list[int],
    target_address_ids: list[int],
) -> None:
    """Create address lineage relationships between all source and target addresses for a pipeline"""
    lineage_relationships = []

    for source_id in source_address_ids:
        for target_id in target_address_ids:
            # Check if relationship already exists for this pipeline
            existing = (
                await session.exec(
                    select(AddressLineage).where(
                        AddressLineage.pipeline_id == pipeline_id,
                        AddressLineage.source_address_id == source_id,
                        AddressLineage.target_address_id == target_id,
                    )
                )
            ).one_or_none()

            if existing is None:
                lineage_relationships.append(
                    {
                        "pipeline_id": pipeline_id,
                        "source_address_id": source_id,
                        "target_address_id": target_id,
                    }
                )

    if lineage_relationships:
        await session.exec(
            AddressLineage.__table__.insert().values(lineage_relationships)
        )
        await session.commit()
        logger.info(
            f"Created {len(lineage_relationships)} address lineage relationships for pipeline {pipeline_id}"
        )


async def _process_address_lists(
    session: Session, source_addresses: list, target_addresses: list, response: Response
) -> tuple[list[int], list[int]]:
    """Process lists of source and target addresses and return their IDs"""
    source_address_ids = []
    target_address_ids = []

    # Process source addresses
    for source_addr in source_addresses:
        source_address_input = AddressPostInput(
            name=source_addr.address_name,
            address_type_name=source_addr.address_type_name,
        )
        source_address = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=source_address_input, response=response
            )
        )
        source_address_ids.append(source_address.id)

    # Process target addresses
    for target_addr in target_addresses:
        target_address_input = AddressPostInput(
            name=target_addr.address_name,
            address_type_name=target_addr.address_type_name,
        )
        target_address = AddressPostOutput(
            **await db_get_or_create_address(
                session=session, address=target_address_input, response=response
            )
        )
        target_address_ids.append(target_address.id)

    return source_address_ids, target_address_ids

import json
import logging

import pendulum
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session

from src.database.address_type_utils import db_get_or_create_address_type
from src.database.models.address import Address
from src.models.address import AddressPatchInput, AddressPostInput, AddressPostOutput
from src.models.address_type import AddressTypePostInput, AddressTypePostOutput

logger = logging.getLogger(__name__)


def generate_address_hash(address_input: AddressPostInput) -> str:
    """Generate a hash of the address input data for change detection.

    This detects when the address data changes and needs to be updated.
    """
    return str(
        hash(
            json.dumps(
                address_input.model_dump(exclude_unset=True),
                sort_keys=True,
                default=str,
            )
        )
    )


async def db_get_or_create_address(
    session: Session, address: AddressPostInput, response: Response
) -> AddressPostOutput:
    """Get existing address id or create new one and return id"""
    created = False
    new_address = Address(**address.model_dump(exclude_unset=True))

    # Generate hash of the input data
    input_hash = generate_address_hash(address)

    # Check if Address record exists
    row = (
        await session.exec(
            select(Address.id, Address.input_hash).where(Address.name == address.name)
        )
    ).one_or_none()

    if row is None:
        logger.info(f"Address '{new_address.name}' Not Found. Creating...")

        # Resolve Pipeline Type Info
        address_type_input = AddressTypePostInput(
            name=address.address_type_name, group_name=address.address_type_group_name
        )
        address_type = AddressTypePostOutput(
            **await db_get_or_create_address_type(
                session=session, address_type=address_type_input, response=response
            )
        )

        if address.address_type_group_name == "database":
            address_parts = address.name.split(".")
            if len(address_parts) == 3:
                new_address.database_name = address_parts[0]
                new_address.schema_name = address_parts[1]
                new_address.table_name = address_parts[2]

        address_stmt = (
            Address.__table__.insert()
            .returning(Address.id)
            .values(
                **new_address.model_dump(exclude={"id"}),
                address_type_id=address_type.id,
                input_hash=input_hash,
            )
        )
        try:
            address_id = (await session.exec(address_stmt)).scalar_one()
            await session.commit()
            created = True
            logger.info(f"Address '{address.name}' Successfully Created")
        except IntegrityError as e:
            await session.rollback()
            if isinstance(e.orig, UniqueViolationError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unique constraint violation",
                )
            else:
                logger.error(f"Database integrity error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database integrity error",
                )
    else:
        address_id = row.id

        # Check if the input data has changed (address data was updated)
        data_changed = row.input_hash != input_hash

        if data_changed:
            logger.info(f"Address '{address.name}' input data has changed. Updating...")

            # Resolve Pipeline Type Info for update
            address_type_input = AddressTypePostInput(
                name=address.address_type_name,
                group_name=address.address_type_group_name,
            )
            address_type = AddressTypePostOutput(
                **await db_get_or_create_address_type(
                    session=session, address_type=address_type_input, response=response
                )
            )

            # Update database fields if it's a database address
            if address.address_type_group_name == "database":
                address_parts = address.name.split(".")
                if len(address_parts) == 3:
                    new_address.database_name = address_parts[0]
                    new_address.schema_name = address_parts[1]
                    new_address.table_name = address_parts[2]

            # Update the address record
            update_stmt = (
                update(Address)
                .where(Address.id == address_id)
                .values(
                    **new_address.model_dump(exclude={"id"}),
                    address_type_id=address_type.id,
                    input_hash=input_hash,
                    updated_at=pendulum.now("UTC"),
                )
            )
            await session.exec(update_stmt)
            await session.commit()
            logger.info(f"Address '{address.name}' successfully updated")
        else:
            pass  # Input data unchanged, no update needed

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": address_id}


async def db_update_address(session: Session, patch: AddressPatchInput) -> Address:
    try:
        address = (
            await session.exec(select(Address).where(Address.id == patch.id))
        ).scalar_one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    address.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        if field == "id":
            continue
        setattr(address, field, value)

    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address

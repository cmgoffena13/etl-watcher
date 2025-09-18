import logging

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlmodel import Session

from src.database.address_type_utils import db_get_or_create_address_type
from src.database.models.address import Address
from src.models.address import AddressPatchInput, AddressPostInput, AddressPostOutput
from src.models.address_type import AddressTypePostInput, AddressTypePostOutput

logger = logging.getLogger(__name__)


async def db_get_or_create_address(
    session: Session, address: AddressPostInput, response: Response
) -> AddressPostOutput:
    """Get existing address id or create new one and return id"""
    created = False
    new_address = Address(**address.model_dump(exclude_unset=True))

    address_id = (
        await session.exec(select(Address.id).where(Address.name == address.name))
    ).scalar_one_or_none()

    if address_id is None:
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
            )
        )
        address_id = (await session.exec(address_stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(f"Address '{address.name}' Successfully Created")

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": address_id}


async def db_update_address(session: Session, patch: AddressPatchInput) -> Address:
    address = (
        await session.exec(select(Address).where(Address.id == patch.id))
    ).scalar_one_or_none()
    if address is None:
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

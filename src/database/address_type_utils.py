import logging

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlmodel import Session

from src.database.models.address_type import AddressType
from src.models.address_type import (
    AddressTypePatchInput,
    AddressTypePostInput,
    AddressTypePostOutput,
)

logger = logging.getLogger(__name__)


async def db_get_or_create_address_type(
    session: Session, address_type: AddressTypePostInput, response: Response
) -> AddressTypePostOutput:
    """Get existing address type id or create new one and return id"""
    created = False

    address_type_id = (
        await session.exec(
            select(AddressType.id).where(AddressType.name == AddressType.name)
        )
    ).scalar_one_or_none()

    if address_type_id is None:
        logger.info(f"Address Type '{address_type.name}' Not Found. Creating...")
        stmt = (
            AddressType.__table__.insert()
            .returning(AddressType.id)
            .values(**address_type.model_dump(exclude={"id"}))
        )
        address_type_id = (await session.exec(stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(f"Address Type '{address_type.name}' Successfully Created")

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": address_type_id}


async def db_update_address_type(
    session: Session, patch: AddressTypePatchInput
) -> AddressType:
    address_type = (
        await session.exec(select(AddressType).where(AddressType.id == patch.id))
    ).scalar_one_or_none()
    if address_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address Type Not Found"
        )

    address_type.updated_at = pendulum.now("UTC")
    for field, value in patch.model_dump(exclude_unset=True).items():
        if field == "id":
            continue
        setattr(address_type, field, value)

    session.add(address_type)
    await session.commit()
    await session.refresh(address_type)
    return address_type

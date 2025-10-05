from fastapi import APIRouter, Response, status
from sqlalchemy import select

from src.database.address_type_utils import (
    db_get_or_create_address_type,
    db_update_address_type,
)
from src.database.models.address_type import AddressType
from src.database.session import SessionDep
from src.models.address_type import (
    AddressTypePatchInput,
    AddressTypePostInput,
    AddressTypePostOutput,
)

router = APIRouter()


@router.post("/address_type", response_model=AddressTypePostOutput)
async def get_or_create_address_type(
    address_type: AddressTypePostInput, response: Response, session: SessionDep
):
    return await db_get_or_create_address_type(
        session=session, address_type=address_type, response=response
    )


@router.get(
    "/address_type", response_model=list[AddressType], status_code=status.HTTP_200_OK
)
async def get_address_types(session: SessionDep):
    return (await session.exec(select(AddressType))).scalars().all()


@router.get(
    "/address_type/{address_type_id}",
    response_model=AddressType,
    status_code=status.HTTP_200_OK,
)
async def get_address_type(address_type_id: int, session: SessionDep):
    return (
        await session.exec(select(AddressType).where(AddressType.id == address_type_id))
    ).scalar_one_or_none()


@router.patch(
    "/address_type", response_model=AddressType, status_code=status.HTTP_200_OK
)
async def update_address_type(address_type: AddressTypePatchInput, session: SessionDep):
    return await db_update_address_type(patch=address_type, session=session)

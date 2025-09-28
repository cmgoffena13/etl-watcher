from fastapi import APIRouter, Response, status
from sqlalchemy import select

from src.database.address_utils import db_get_or_create_address, db_update_address
from src.database.models.address import Address
from src.database.session import SessionDep
from src.models.address import (
    AddressPatchInput,
    AddressPostInput,
    AddressPostOutput,
)

router = APIRouter()


@router.post("/address", response_model=AddressPostOutput)
async def get_or_create_address(
    address: AddressPostInput, response: Response, session: SessionDep
):
    return await db_get_or_create_address(
        session=session, address=address, response=response
    )


@router.get("/address", response_model=list[Address], status_code=status.HTTP_200_OK)
async def get_addresses(session: SessionDep):
    return (await session.exec(select(Address))).scalars().all()


@router.patch("/address", response_model=Address, status_code=status.HTTP_200_OK)
async def update_address(address: AddressPatchInput, session: SessionDep):
    return await db_update_address(session=session, patch=address)

from typing import List

from fastapi import APIRouter, Response, status

from src.database.address_lineage_utils import (
    db_create_address_lineage,
    db_get_address_lineage_for_address,
)
from src.database.models.address_lineage import AddressLineage
from src.database.session import SessionDep
from src.models.address_lineage import (
    AddressLineageClosureOutput,
    AddressLineagePostInput,
    AddressLineagePostOutput,
)

router = APIRouter()


@router.post(
    "/address_lineage",
    response_model=AddressLineagePostOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_address_lineage(
    lineage_input: AddressLineagePostInput, response: Response, session: SessionDep
):
    return await db_create_address_lineage(
        session=session, lineage_input=lineage_input, response=response
    )


@router.get(
    "/address_lineage/{address_id}",
    response_model=List[AddressLineageClosureOutput],
)
async def get_address_lineage_for_address(address_id: int, session: SessionDep):
    results = await db_get_address_lineage_for_address(
        session=session, address_id=address_id
    )
    return [
        AddressLineageClosureOutput(
            source_address_id=row[0],
            target_address_id=row[1],
            depth=row[2],
            source_address_name=row[3],
            target_address_name=row[4],
        )
        for row in results
    ]

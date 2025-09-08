from typing import List

from fastapi import APIRouter, Response, status

from src.database.address_lineage_utils import (
    db_create_address_lineage,
    db_get_address_lineage_by_pipeline,
)
from src.database.models.address_lineage import AddressLineage
from src.database.session import SessionDep
from src.models.address_lineage import (
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
    "/address_lineage/{pipeline_id}",
    response_model=List[AddressLineage],
)
async def get_address_lineage_by_pipeline(pipeline_id: int, session: SessionDep):
    return await db_get_address_lineage_by_pipeline(
        session=session, pipeline_id=pipeline_id
    )

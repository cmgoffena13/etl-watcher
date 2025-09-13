from fastapi import APIRouter, Response, status

from src.database.freshness_utils import db_check_pipeline_freshness
from src.database.session import SessionDep
from src.models.freshness import FreshnessPostOutput

router = APIRouter()


@router.post(
    "/freshness", response_model=FreshnessPostOutput, status_code=status.HTTP_200_OK
)
async def check_freshness(session: SessionDep):
    return await db_check_pipeline_freshness(session=session)

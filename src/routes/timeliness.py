from fastapi import APIRouter, Response, status

from src.database.session import SessionDep
from src.database.timeliness_utils import db_check_pipeline_execution_timeliness
from src.models.timeliness import TimelinessPostInput, TimelinessPostOutput

router = APIRouter()


@router.post(
    "/timeliness", response_model=TimelinessPostOutput, status_code=status.HTTP_200_OK
)
async def check_timeliness(
    input: TimelinessPostInput, response: Response, session: SessionDep
):
    return await db_check_pipeline_execution_timeliness(
        session=session, response=response, lookback_minutes=input.lookback_minutes
    )

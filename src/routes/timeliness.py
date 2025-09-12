from fastapi import APIRouter, Response, status

from src.database.session import SessionDep
from src.database.timeliness_utils import db_check_timeliness
from src.models.timeliness import TimelinessPostOutput

router = APIRouter()


@router.post(
    "/timeliness", response_model=TimelinessPostOutput, status_code=status.HTTP_200_OK
)
async def check_timeliness(response: Response, session: SessionDep):
    return await db_check_timeliness(session=session, response=response)

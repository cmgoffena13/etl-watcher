from fastapi import APIRouter, Response, status

from src.celery_tasks import timeliness_check_task
from src.database.session import SessionDep
from src.models.timeliness import TimelinessPostInput, TimelinessPostOutput

router = APIRouter()


@router.post(
    "/timeliness", response_model=TimelinessPostOutput, status_code=status.HTTP_200_OK
)
async def check_timeliness(
    input: TimelinessPostInput, response: Response, session: SessionDep
):
    # Queue the timeliness check as a Celery task
    timeliness_check_task.delay(lookback_minutes=input.lookback_minutes)

    return {"status": "queued"}

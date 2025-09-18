from fastapi import APIRouter, status

from src.celery_tasks import freshness_check_task
from src.database.session import SessionDep
from src.models.freshness import FreshnessPostOutput

router = APIRouter()


@router.post(
    "/freshness", response_model=FreshnessPostOutput, status_code=status.HTTP_200_OK
)
async def check_freshness(session: SessionDep):
    # Queue the freshness check as a Celery task
    freshness_check_task.delay()

    return {"status": "queued"}

from fastapi import APIRouter, status

from src.celery_tasks import freshness_check_task
from src.models.freshness import FreshnessPostOutput

router = APIRouter()


@router.post(
    "/freshness", response_model=FreshnessPostOutput, status_code=status.HTTP_200_OK
)
async def check_freshness():
    # Queue the freshness check as a Celery task
    freshness_check_task.delay()

    return {"status": "queued"}

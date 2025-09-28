import asyncio
import logging

import redis
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from src.notifier import AlertLevel, send_slack_message
from src.settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/celery/monitor-queue")
async def check_celery_queue():
    """Monitor Celery queue depths and alert if queue gets too big"""
    try:
        redis_client = redis.Redis.from_url(config.REDIS_URL)

        queue_name = "celery"

        # Run Redis operations in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        messages = await loop.run_in_executor(None, redis_client.llen, queue_name)
        scheduled = await loop.run_in_executor(
            None, redis_client.zcard, f"{queue_name}:scheduled"
        )
        total_pending = messages + scheduled

        if total_pending >= 100:
            alert_level = AlertLevel.CRITICAL
        elif total_pending >= 50:
            alert_level = AlertLevel.WARNING
        else:
            logger.info(
                f"Queue monitoring completed - {total_pending} tasks in queue (healthy)"
            )
            return {"status": "success"}

        try:
            details = {
                "Messages in queue": messages,
                "Scheduled tasks": scheduled,
                "Total pending": total_pending,
            }

            await send_slack_message(
                level=alert_level,
                title=f"Celery Queue Alert",
                message=f"Queue has {total_pending} pending tasks",
                details=details,
            )
        except Exception as alert_error:
            logger.error(f"Failed to send Slack alert for celery queue: {alert_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send Slack alert for celery queue: {alert_error}",
            )

        logger.warning(f"Queue monitoring completed - {total_pending} tasks in queue")

    except Exception as e:
        logger.error(f"Queue monitoring failed: {e}")
        return {"status": "error"}

    return {"status": "success"}

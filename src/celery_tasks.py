# src/celery_tasks.py
import asyncio

from src.celery_app import celery
from src.database.anomaly_detection_utils import db_detect_anomalies_for_pipeline
from src.database.freshness_utils import db_check_pipeline_freshness
from src.database.session import get_session
from src.database.timeliness_utils import db_check_pipeline_execution_timeliness


@celery.task(bind=True, rate_limit="5/s", max_retries=3)
def detect_anomalies_task(self, pipeline_id: int, pipeline_execution_id: int):
    """Rate-limited anomaly detection task"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting anomaly detection..."}
        )
        asyncio.run(_run_async_anomaly_detection(pipeline_id, pipeline_execution_id))
        self.update_state(
            state="SUCCESS", meta={"status": "Anomaly detection completed"}
        )
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        self.retry(countdown=60 * (2**self.request.retries), exc=exc)


async def _run_async_anomaly_detection(pipeline_id: int, pipeline_execution_id: int):
    async for session in get_session():
        await db_detect_anomalies_for_pipeline(
            session, pipeline_id, pipeline_execution_id
        )
        break


@celery.task(bind=True, rate_limit="2/s", max_retries=2)
def timeliness_check_task(self, lookback_minutes: int = 60):
    """Rate-limited timeliness check task"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting timeliness check..."}
        )
        asyncio.run(_run_async_timeliness_check(lookback_minutes))
        self.update_state(
            state="SUCCESS", meta={"status": "Timeliness check completed"}
        )
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        self.retry(countdown=300, exc=exc)


async def _run_async_timeliness_check(lookback_minutes: int):
    async for session in get_session():
        await db_check_pipeline_execution_timeliness(session, None, lookback_minutes)
        break


@celery.task(bind=True, rate_limit="2/s", max_retries=2)
def freshness_check_task(self):
    """Rate-limited freshness check task"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting freshness check..."}
        )
        asyncio.run(_run_async_freshness_check())
        self.update_state(state="SUCCESS", meta={"status": "Freshness check completed"})
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        self.retry(countdown=300, exc=exc)


async def _run_async_freshness_check():
    async for session in get_session():
        await db_check_pipeline_freshness(session)
        break

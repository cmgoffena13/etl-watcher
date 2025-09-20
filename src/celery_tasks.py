# src/celery_tasks.py
import logging

from asgiref.sync import async_to_sync  # So annoying
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_app import celery
from src.database.anomaly_detection_utils import db_detect_anomalies_for_pipeline
from src.database.freshness_utils import db_check_pipeline_freshness
from src.database.timeliness_utils import db_check_pipeline_execution_timeliness
from src.settings import get_database_config

logger = logging.getLogger(__name__)


@celery.task(bind=True, rate_limit="5/s", max_retries=3, default_retry_delay=60)
def detect_anomalies_task(self, pipeline_id: int, pipeline_execution_id: int):
    """Rate-limited anomaly detection task with retries"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting anomaly detection..."}
        )

        result = async_to_sync(_run_async_anomaly_detection)(
            pipeline_id, pipeline_execution_id
        )

        self.update_state(
            state="SUCCESS", meta={"status": "Anomaly detection completed"}
        )
        return result

    except Exception as exc:
        logger.error(f"Anomaly detection failed: {exc}")

        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries,
            },
        )
        raise self.retry(exc=exc)


async def _run_async_anomaly_detection(pipeline_id: int, pipeline_execution_id: int):
    """Async function that creates its own database connection"""
    db_config = get_database_config()
    engine = create_async_engine(
        url=db_config["sqlalchemy.url"],
        echo=db_config["sqlalchemy.echo"],
        future=db_config["sqlalchemy.future"],
        connect_args=db_config.get("sqlalchemy.connect_args", {}),
        pool_size=1,
        max_overflow=0,
    )

    try:
        celery_sessionmaker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with celery_sessionmaker() as session:
            await db_detect_anomalies_for_pipeline(
                session, pipeline_id, pipeline_execution_id
            )
        return {"status": "success", "message": "Anomaly detection completed"}
    finally:
        await engine.dispose()


@celery.task(bind=True, rate_limit="2/s", max_retries=3, default_retry_delay=60)
def timeliness_check_task(self, lookback_minutes: int = 60):
    """Rate-limited timeliness check task with retries"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting timeliness check..."}
        )

        result = async_to_sync(_run_async_timeliness_check)(lookback_minutes)

        self.update_state(
            state="SUCCESS", meta={"status": "Timeliness check completed"}
        )
        return result

    except Exception as exc:
        logger.error(f"Timeliness check failed: {exc}")

        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries,
            },
        )
        raise self.retry(exc=exc)


async def _run_async_timeliness_check(lookback_minutes: int):
    """Async function that creates its own database connection"""
    db_config = get_database_config()
    engine = create_async_engine(
        url=db_config["sqlalchemy.url"],
        echo=db_config["sqlalchemy.echo"],
        future=db_config["sqlalchemy.future"],
        connect_args=db_config.get("sqlalchemy.connect_args", {}),
        pool_size=1,
        max_overflow=0,
    )

    try:
        celery_sessionmaker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with celery_sessionmaker() as session:
            await db_check_pipeline_execution_timeliness(
                session, None, lookback_minutes
            )
        return {"status": "success", "message": "Timeliness check completed"}
    finally:
        await engine.dispose()


@celery.task(bind=True, rate_limit="2/s", max_retries=3, default_retry_delay=60)
def freshness_check_task(self):
    """Rate-limited freshness check task with retries"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting freshness check..."}
        )

        result = async_to_sync(_run_async_freshness_check)()

        self.update_state(state="SUCCESS", meta={"status": "Freshness check completed"})
        return result

    except Exception as exc:
        logger.error(f"Freshness check failed: {exc}")

        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries,
            },
        )
        raise self.retry(exc=exc)


async def _run_async_freshness_check():
    """Async function that creates its own database connection"""
    db_config = get_database_config()
    engine = create_async_engine(
        url=db_config["sqlalchemy.url"],
        echo=db_config["sqlalchemy.echo"],
        future=db_config["sqlalchemy.future"],
        connect_args=db_config.get("sqlalchemy.connect_args", {}),
        pool_size=1,
        max_overflow=0,
    )

    try:
        celery_sessionmaker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with celery_sessionmaker() as session:
            await db_check_pipeline_freshness(session)
        return {"status": "success", "message": "Freshness check completed"}
    finally:
        await engine.dispose()

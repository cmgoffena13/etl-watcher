# src/celery_tasks.py
import structlog
from asgiref.sync import async_to_sync  # So annoying
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_app import celery
from src.database.address_lineage_utils import db_rebuild_closure_table_incremental
from src.database.anomaly_detection_utils import (
    db_detect_anomalies_for_pipeline_execution,
)
from src.database.freshness_utils import db_check_pipeline_freshness
from src.database.pipeline_execution_utils import (
    db_maintain_pipeline_execution_closure_table,
)
from src.database.timeliness_utils import db_check_pipeline_execution_timeliness
from src.notifier import AlertLevel, send_slack_message
from src.settings import config, get_database_config

logger = structlog.get_logger(__name__)


@celery.task(bind=True, rate_limit="15/s", max_retries=3, default_retry_delay=60)
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
            await db_detect_anomalies_for_pipeline_execution(
                session, pipeline_id, pipeline_execution_id
            )
        return {"status": "success", "message": "Anomaly detection completed"}
    finally:
        await engine.dispose()


@celery.task(bind=True, rate_limit="1/s", max_retries=3, default_retry_delay=60)
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


@celery.task(bind=True, rate_limit="1/s", max_retries=3, default_retry_delay=60)
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


@celery.task(bind=True, rate_limit="5/s", max_retries=3, default_retry_delay=60)
def address_lineage_closure_rebuild_task(
    self, connected_addresses: list[int], pipeline_id: int
):
    """Rate-limited closure table rebuild task with retries"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Starting closure table rebuild..."}
        )

        result = async_to_sync(_run_async_address_lineage_closure_rebuild)(
            connected_addresses, pipeline_id
        )

        self.update_state(
            state="SUCCESS", meta={"status": "Closure table rebuild completed"}
        )
        return result

    except Exception as exc:
        logger.error(f"Closure table rebuild failed: {exc}")

        # Send Slack notification only on final failure (no more retries left)
        if self.request.retries >= self.max_retries - 1:
            send_slack_message(
                level=AlertLevel.ERROR,
                title="Address Lineage Closure Table Rebuild Failed",
                message=f"Pipeline {pipeline_id} failed to rebuild closure table after {self.max_retries} retries: {str(exc)}",
                details={
                    "pipeline_id": pipeline_id,
                    "connected_addresses": connected_addresses,
                    "error_type": type(exc).__name__,
                    "retry_count": self.request.retries,
                    "max_retries": self.max_retries,
                },
            )

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


async def _run_async_address_lineage_closure_rebuild(
    connected_addresses: list[int], pipeline_id: int
):
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
            await db_rebuild_closure_table_incremental(
                session, set(connected_addresses), pipeline_id
            )
        return {"status": "success", "message": "Closure table rebuild completed"}
    finally:
        await engine.dispose()


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def pipeline_execution_closure_maintain_task(self, execution_id: int, parent_id: int):
    """Maintain pipeline execution closure table for a new execution"""
    try:
        self.update_state(
            state="PROGRESS", meta={"status": "Maintaining execution closure table..."}
        )

        result = async_to_sync(_run_async_pipeline_execution_closure_maintenance)(
            execution_id, parent_id
        )

        self.update_state(
            state="SUCCESS", meta={"status": "Execution closure table maintained"}
        )
        return result

    except Exception as exc:
        logger.error(f"Execution closure table maintenance failed: {exc}")

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


async def _run_async_pipeline_execution_closure_maintenance(
    execution_id: int, parent_id: int
):
    """Async function that maintains execution closure table"""

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
            await db_maintain_pipeline_execution_closure_table(
                session, execution_id, parent_id
            )
        return {"status": "success", "message": "Execution closure table maintained"}
    finally:
        await engine.dispose()


# ============================================================================
# SCHEDULED TASKS
# ============================================================================


@celery.task(bind=True, max_retries=3, default_retry_delay=60, queue="scheduled")
def scheduled_freshness_check(self):
    """Scheduled task to check freshness for all active pipelines"""
    return freshness_check_task.delay()


@celery.task(bind=True, max_retries=3, default_retry_delay=60, queue="scheduled")
def scheduled_timeliness_check(self):
    """Scheduled task to check timeliness for all active pipelines"""
    return timeliness_check_task.delay(
        lookback_minutes=config.WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES
    )


@celery.task(bind=True, max_retries=3, default_retry_delay=60, queue="scheduled")
def scheduled_celery_queue_health_check(self):
    """Scheduled task to monitor queue health and send alerts"""
    # Import here to avoid circular import
    from src.routes.celery import check_celery_queue

    return async_to_sync(check_celery_queue)()

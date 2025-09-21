# src/celery_tasks.py
import asyncio
import logging

from asgiref.sync import async_to_sync  # So annoying
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_app import celery
from src.database.anomaly_detection_utils import db_detect_anomalies_for_pipeline
from src.database.freshness_utils import db_check_pipeline_freshness
from src.database.timeliness_utils import db_check_pipeline_execution_timeliness
from src.notifier import AlertLevel, send_slack_message
from src.settings import get_database_config

logger = logging.getLogger(__name__)


@celery.task(bind=True, rate_limit="10/s", max_retries=3, default_retry_delay=60)
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


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def monitor_celery_queues_task(self):
    """Monitor Celery queue depths and alert if queue get too big"""
    try:
        self.update_state(state="PROGRESS", meta={"status": "Checking queue depths..."})

        inspect = celery.control.inspect()
        active_queues = inspect.active_queues()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()

        if not active_queues:
            logger.warning("No active workers found for queue monitoring")
            return {"status": "success", "message": "No workers to monitor"}

        queue_data = {}
        total_workers = len(active_queues)

        for worker_name, queues in active_queues.items():
            for queue_info in queues:
                queue_name = queue_info.get("name", "default")
                messages = queue_info.get("messages", 0)

                if queue_name not in queue_data:
                    queue_data[queue_name] = {
                        "messages": 0,
                        "workers": 0,
                        "scheduled": 0,
                        "reserved": 0,
                    }

                queue_data[queue_name]["messages"] = max(
                    queue_data[queue_name]["messages"], messages
                )
                queue_data[queue_name]["workers"] += 1

                if scheduled_tasks:
                    queue_data[queue_name]["scheduled"] += len(
                        scheduled_tasks.get(worker_name, [])
                    )
                if reserved_tasks:
                    queue_data[queue_name]["reserved"] += len(
                        reserved_tasks.get(worker_name, [])
                    )

        alerts_sent = 0
        for queue_name, data in queue_data.items():
            messages = data["messages"]
            reserved_count = data["reserved"]
            total_pending = messages + reserved_count

            if messages >= 100:
                alert_level = AlertLevel.CRITICAL
            elif messages >= 50:
                alert_level = AlertLevel.WARNING
            elif messages >= 20:
                alert_level = AlertLevel.INFO
            else:
                continue

            try:
                asyncio.run(
                    send_slack_message(
                        level=alert_level,
                        title="Celery Queue Alert",
                        message=f"Queue '{queue_name}' has {messages} pending messages",
                        details={
                            "Active Workers": str(total_workers),
                            "Waiting in Queue": str(messages),
                            "Ready to Process - Waiting on Worker": str(reserved_count),
                            "Total Backlog": str(total_pending),
                        },
                    )
                )
                logger.info(f"Sent queue alert for '{queue_name}': {messages} messages")
                alerts_sent += 1
            except Exception as e:
                logger.error(f"Failed to send queue alert: {e}")

        self.update_state(
            state="SUCCESS",
            meta={
                "status": "Queue monitoring completed",
                "alerts_sent": alerts_sent,
                "queues_checked": sum(len(queues) for queues in active_queues.values()),
            },
        )

        return {
            "status": "success",
            "message": f"Queue monitoring completed, {alerts_sent} alerts sent",
        }

    except Exception as exc:
        logger.error(f"Queue monitoring failed: {exc}")
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

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

        # Run Redis operations in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        # Check both regular and scheduled queues
        regular_queue = "celery"
        scheduled_queue = "scheduled"

        # Get messages from both queues
        regular_messages = await loop.run_in_executor(
            None, redis_client.lrange, regular_queue, 0, -1
        )
        scheduled_messages = await loop.run_in_executor(
            None, redis_client.lrange, scheduled_queue, 0, -1
        )

        # Get scheduled tasks count (from Redis beat scheduler - these are cron jobs waiting to run)
        beat_scheduled_tasks = await loop.run_in_executor(
            None, redis_client.zcard, f"{regular_queue}:scheduled"
        )

        # Count tasks by type for both queues
        task_counts = {
            "detect_anomalies_task": 0,
            "timeliness_check_task": 0,
            "freshness_check_task": 0,
            "address_lineage_closure_rebuild_task": 0,
            "pipeline_execution_closure_maintain_task": 0,
            "scheduled_freshness_check": 0,
            "scheduled_timeliness_check": 0,
            "scheduled_queue_health_check": 0,
            "unknown": 0,
        }

        # Analyze regular queue messages
        for message in regular_messages:
            try:
                import json

                task_data = json.loads(message)

                # Task name is in headers.task, not at the root level
                headers = task_data.get("headers", {})
                task_name = headers.get("task", "unknown")

                # Map task names to our known tasks
                # Celery uses full module paths like 'src.celery_tasks.detect_anomalies_task'
                if "detect_anomalies_task" in task_name:
                    task_counts["detect_anomalies_task"] += 1
                elif "timeliness_check_task" in task_name:
                    task_counts["timeliness_check_task"] += 1
                elif "freshness_check_task" in task_name:
                    task_counts["freshness_check_task"] += 1
                elif "address_lineage_closure_rebuild_task" in task_name:
                    task_counts["address_lineage_closure_rebuild_task"] += 1
                elif "pipeline_execution_closure_maintain_task" in task_name:
                    task_counts["pipeline_execution_closure_maintain_task"] += 1
                else:
                    task_counts["unknown"] += 1
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse task message: {e}")
                task_counts["unknown"] += 1

        # Analyze scheduled queue messages
        for message in scheduled_messages:
            try:
                import json

                task_data = json.loads(message)

                # Task name is in headers.task, not at the root level
                headers = task_data.get("headers", {})
                task_name = headers.get("task", "unknown")

                # Map scheduled task names
                if "scheduled_freshness_check" in task_name:
                    task_counts["scheduled_freshness_check"] += 1
                elif "scheduled_timeliness_check" in task_name:
                    task_counts["scheduled_timeliness_check"] += 1
                elif "scheduled_queue_health_check" in task_name:
                    task_counts["scheduled_queue_health_check"] += 1
                else:
                    task_counts["unknown"] += 1
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse scheduled queue message: {e}")
                task_counts["unknown"] += 1

        total_pending = (
            len(regular_messages) + len(scheduled_messages) + beat_scheduled_tasks
        )

        if total_pending >= 100:
            alert_level = AlertLevel.CRITICAL
        elif total_pending >= 50:
            alert_level = AlertLevel.WARNING
        else:
            logger.info(
                f"Queue monitoring completed - {total_pending} tasks in queue (healthy)"
            )
            # Format task breakdown for better readability
            task_breakdown_formatted = []
            for task_name, count in task_counts.items():
                if count > 0:
                    # Convert snake_case to readable format
                    readable_name = task_name.replace("_", " ").title()
                    task_breakdown_formatted.append(f"{readable_name}: {count}")

            return {
                "status": "success",
                "total_pending": total_pending,
                "regular_queue_pending": len(regular_messages),
                "scheduled_queue_pending": len(scheduled_messages),
                "beat_scheduled_tasks": beat_scheduled_tasks,
                "task_breakdown": task_breakdown_formatted,
                "task_breakdown_raw": task_counts,  # Keep raw data for programmatic use
            }

        try:
            # Format task breakdown for better readability
            task_breakdown_formatted = []
            for task_name, count in task_counts.items():
                if count > 0:
                    # Convert snake_case to readable format
                    readable_name = task_name.replace("_", " ").title()
                    task_breakdown_formatted.append(f"{readable_name}: {count}")

            details = {
                "Total pending": total_pending,
                "Regular queue": len(regular_messages),
                "Scheduled queue": len(scheduled_messages),
                "Beat scheduled tasks": beat_scheduled_tasks,
                "Task breakdown": task_breakdown_formatted,
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

    # Format task breakdown for better readability
    task_breakdown_formatted = []
    for task_name, count in task_counts.items():
        if count > 0:
            # Convert snake_case to readable format
            readable_name = task_name.replace("_", " ").title()
            task_breakdown_formatted.append(f"{readable_name}: {count}")

    return {
        "status": "success",
        "total_pending": total_pending,
        "scheduled_tasks": scheduled_tasks,
        "task_breakdown": task_breakdown_formatted,
        "task_breakdown_raw": task_counts,  # Keep raw data for programmatic use
    }

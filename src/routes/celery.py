import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.celery_app import celery
from src.celery_tasks import monitor_celery_queues_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/celery/ws/workers")
async def websocket_worker_monitor(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(1)  # Don't block the event loop!

            inspect = celery.control.inspect()
            try:
                active_tasks = inspect.active() or {}
                reserved_tasks = inspect.reserved() or {}
                scheduled_tasks = inspect.scheduled() or {}
                stats = inspect.stats() or {}
                active_queues = inspect.active_queues() or {}
            except Exception as e:
                logger.warning(f"Failed to get worker stats: {e}")
                active_tasks = {}
                reserved_tasks = {}
                scheduled_tasks = {}
                stats = {}
                active_queues = {}

            # Build monitoring data
            worker_data = {}
            total_active = 0
            total_reserved = 0
            total_scheduled = 0
            queue_data = {}

            if active_tasks:
                for worker_name, tasks in active_tasks.items():
                    worker_data[worker_name] = {
                        "name": worker_name,
                        "active_tasks": len(tasks),
                        "tasks": tasks,
                        "status": "busy" if tasks else "idle",
                    }
                    total_active += len(tasks)

            if reserved_tasks:
                for worker_name, tasks in reserved_tasks.items():
                    if worker_name not in worker_data:
                        worker_data[worker_name] = {
                            "name": worker_name,
                            "active_tasks": 0,
                            "tasks": [],
                            "status": "idle",
                        }
                    worker_data[worker_name]["reserved_tasks"] = len(tasks)
                    total_reserved += len(tasks)

            if scheduled_tasks:
                for worker_name, tasks in scheduled_tasks.items():
                    if worker_name not in worker_data:
                        worker_data[worker_name] = {
                            "name": worker_name,
                            "active_tasks": 0,
                            "tasks": [],
                            "status": "idle",
                        }
                    worker_data[worker_name]["scheduled_tasks"] = len(tasks)
                    total_scheduled += len(tasks)

            # Process queue data
            if active_queues:
                for worker_name, queues in active_queues.items():
                    for queue_info in queues:
                        queue_name = queue_info.get("name", "default")
                        if queue_name not in queue_data:
                            queue_data[queue_name] = {
                                "name": queue_name,
                                "messages": 0,
                                "workers": set(),
                            }
                        queue_data[queue_name]["messages"] += queue_info.get(
                            "messages", 0
                        )
                        queue_data[queue_name]["workers"].add(worker_name)

            # Convert sets to lists for JSON serialization
            for queue in queue_data.values():
                queue["workers"] = list(queue["workers"])

            # Add worker stats
            if stats:
                for worker_name, worker_stats in stats.items():
                    if worker_name in worker_data:
                        worker_data[worker_name].update(
                            {
                                "total_tasks": worker_stats.get("total", {}).get(
                                    "src.celery_tasks.detect_anomalies_task", 0
                                ),
                                "pool": worker_stats.get("pool", {}),
                                "rusage": worker_stats.get("rusage", {}),
                            }
                        )

            await websocket.send_json(
                {
                    "timestamp": asyncio.get_event_loop().time(),
                    "total_workers": len(worker_data),
                    "total_active_tasks": total_active,
                    "total_reserved_tasks": total_reserved,
                    "total_scheduled_tasks": total_scheduled,
                    "workers": list(worker_data.values()),
                    "queues": list(queue_data.values()),
                }
            )

            await asyncio.sleep(10)  # Update every 10 seconds

    except WebSocketDisconnect:
        logger.info("Client disconnected from worker monitor")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@router.get("/celery/monitoring", include_in_schema=False)
async def celery_monitoring_dashboard():
    """Real-time Celery worker monitoring dashboard"""
    try:
        with open("src/templates/celery_monitoring.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Celery monitoring page not found</h1>", status_code=404
        )


@router.post("/celery/monitor-queue")
async def trigger_celery_queue_monitoring():
    """Trigger Celery queue monitoring task"""
    try:
        task = monitor_celery_queues_task.delay()

        return {
            "status": "success",
            "message": "Queue monitoring task triggered",
            "task_id": task.id,
            "task_status": "PENDING",
        }
    except Exception as e:
        logger.error(f"Failed to trigger queue monitoring: {e}")
        return {
            "status": "error",
            "message": f"Failed to trigger queue monitoring: {str(e)}",
        }

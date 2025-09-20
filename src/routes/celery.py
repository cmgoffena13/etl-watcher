import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.celery_app import celery

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
                stats = inspect.stats() or {}
            except Exception as e:
                logger.warning(f"Failed to get worker stats: {e}")
                active_tasks = {}
                reserved_tasks = {}
                stats = {}

            # Build monitoring data
            worker_data = {}
            total_active = 0
            total_reserved = 0

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
                    "workers": list(worker_data.values()),
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

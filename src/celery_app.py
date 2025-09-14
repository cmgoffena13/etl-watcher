# src/celery_app.py
from celery import Celery

from src.settings import config

celery = Celery(
    "watcher",
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/1",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/1",
    include=["src.celery_tasks"],
)

# Rate limiting for database protection
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,  # Default: 1
    worker_max_tasks_per_child=1000,  # Restart worker after N tasks
    worker_disable_rate_limits=False,  # Disable rate limits
)

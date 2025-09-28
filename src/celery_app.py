import logfire
from celery import Celery
from celery.signals import worker_init

from src.logging_conf import configure_logging
from src.settings import config


@worker_init.connect()
def init_worker(*args, **kwargs):
    configure_logging()
    logfire.instrument_celery()


celery = Celery(
    "watcher",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
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

import logging
import time
from collections import namedtuple

import logfire
import redis
from celery import Celery
from celery.signals import task_postrun, task_prerun, worker_init

from src.logging_conf import configure_logging
from src.settings import config

logger = logging.getLogger(__name__)

# In-memory tracking
tasks = {}
task_avg_time = {}
Average = namedtuple("Average", "avg_duration count")


@worker_init.connect()
def init_worker(*args, **kwargs):
    configure_logging()
    logfire.instrument_celery()


@task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **kwds):
    """Record task start time in memory"""
    tasks[task_id] = time.time()


@task_postrun.connect
def task_postrun_handler(
    signal, sender, task_id, task, args, kwargs, retval, state, **kwds
):
    """Calculate task duration and update running averages"""
    try:
        cost = time.time() - tasks.pop(task_id)
    except KeyError:
        cost = None

    if not cost:
        return

    try:
        avg_duration, count = task_avg_time[task.name]
        new_count = count + 1
        new_avg = ((avg_duration * count) + cost) / new_count
        task_avg_time[task.name] = Average(new_avg, new_count)
    except KeyError:
        task_avg_time[task.name] = Average(cost, 1)

    # Write aggregated data to Redis
    try:
        r = redis.Redis.from_url(config.REDIS_URL)
        r.hset(
            "celery_task_averages",
            task.name,
            f"{task_avg_time[task.name].avg_duration:.6f},{task_avg_time[task.name].count}",
        )
    except Exception as e:
        logger.warning(f"Error writing task averages to Redis: {e}")


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

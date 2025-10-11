from watcher import Watcher

watcher = Watcher("http://localhost:8000")

watcher.trigger_timeliness_check(lookback_minutes=60)
watcher.trigger_freshness_check()
watcher.trigger_celery_queue_check()

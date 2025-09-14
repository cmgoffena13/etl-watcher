import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 50
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 jitter
# This helps prevent memory leaks in long-running processes
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "watcher"

# Worker timeout
timeout = 60
keepalive = 2

# Graceful restart
graceful_timeout = 30

#!/bin/bash

PORT=${PORT:-8000}
CPU_COUNT=$(nproc)
WORKERS=$((CPU_COUNT * 2 + 1))

granian \
  --interface asgi \
  --host 0.0.0.0 \
  --port $PORT \
  --backlog 2048 \
  --workers $WORKERS \
  --backpressure 50 \
  --log-level info \
  --access-log \
  --access-log-fmt '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' \
  src.app:app

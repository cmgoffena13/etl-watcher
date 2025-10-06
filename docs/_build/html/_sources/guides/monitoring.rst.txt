Monitoring & Health Checks
============================

This guide covers how to set up comprehensive monitoring for your Watcher instance.
Watcher provides multiple monitoring capabilities to ensure your data pipelines are running optimally:

- **Freshness Monitoring** Track data staleness and DML operations
- **Timeliness Monitoring** Validate pipeline execution timing
- **Queue Monitoring** Track Celery task queue depth and performance

Freshness Monitoring
--------------------

Purpose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Freshness monitoring tracks when data was last modified to detect stale data:

- **DML Operations** Monitors inserts, updates, and soft deletes
- **Staleness Detection** Identifies data that hasn't had DML activity recently
- **Alerting** Notifies when data becomes stale

Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure freshness monitoring in pipeline creation:

.. code-block:: json

   {
     "name": "Customer Data Pipeline",
     "pipeline_type_name": "extraction",
     "freshness_number": 24,
     "freshness_datepart": "hour",
     "mute_freshness_check": false
   }

**Freshness Settings**

- **freshness_number**: Time threshold (e.g., 24)
- **freshness_datepart**: Time unit (hour, day, week, month, quarter, year)
- **mute_freshness_check**: Disable freshness monitoring

Supported Time Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **hour**
- **day**
- **week**
- **month**
- **quarter**
- **year**

Running Freshness Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trigger freshness checks manually:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         response = requests.post("http://localhost:8000/freshness")
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             response = client.post("http://localhost:8000/freshness")
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/freshness"

   .. tab:: HTTPie

      .. code-block:: bash

         http POST localhost:8000/freshness

**Response:**

.. code-block:: json

   {
     "status": "queued"
   }

The check runs as a background Celery task and monitors all configured pipelines.

Timeliness Monitoring
---------------------

Purpose
~~~~~~~

Timeliness monitoring validates that pipeline executions complete within expected timeframes:

- **Execution Timing** Tracks how long pipelines take to complete
- **Threshold Validation** Compares against configured timeliness thresholds
- **Performance Issues** Identifies slow or stuck pipelines

Configuration
~~~~~~~~~~~~~

Configure timeliness monitoring in pipeline creation:

.. code-block:: json

   {
     "name": "Critical Data Pipeline",
     "pipeline_type_name": "extraction",
     "timeliness_number": 2,
     "timeliness_datepart": "hour",
     "mute_timeliness_check": false
   }

**Timeliness Settings**

- **timeliness_number** Time threshold (e.g., 2)
- **timeliness_datepart** Time unit (hour, day, week, month, quarter, year)
- **mute_timeliness_check** Disable timeliness monitoring

Running Timeliness Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trigger timeliness checks with lookback period:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         response = requests.post(
             "http://localhost:8000/timeliness",
             json={"lookback_minutes": 60}
         )
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             response = client.post(
                 "http://localhost:8000/timeliness",
                 json={"lookback_minutes": 60}
             )
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/timeliness" \
              -H "Content-Type: application/json" \
              -d '{
                "lookback_minutes": 60
              }'

   .. tab:: HTTPie

      .. code-block:: bash

         http POST localhost:8000/timeliness \
              lookback_minutes=60

**Response:**

.. code-block:: json

   {
     "status": "queued"
   }

**Lookback Period** How far back to look for executions (in minutes)

Queue Monitoring
----------------

Celery Queue Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Celery queue health and performance:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         response = requests.post("http://localhost:8000/celery/monitor-queue")
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             response = client.post("http://localhost:8000/celery/monitor-queue")
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/celery/monitor-queue"

   .. tab:: HTTPie

      .. code-block:: bash

         http POST localhost:8000/celery/monitor-queue

**Response:**

.. code-block:: json

   {
     "status": "success",
     "message": "Queue monitoring completed",
     "queues_checked": 1,
     "total_messages": 0
   }

Alert Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure alert thresholds for queue monitoring:

- **INFO** (20+ messages): Queue building up
- **WARNING** (50+ messages): Queue getting backed up
- **CRITICAL** (100+ messages): Queue severely backed up

Example Alert
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   🚨 CRITICAL
   Celery Queue Alert
   Timestamp: 2025-09-28 06:04:26 UTC
   Message: Queue has 2367 pending tasks
   
   Details:
   • Messages in queue: 2367
   • Scheduled tasks: 0
   • Total pending: 2367

System Health Monitoring
------------------------

Diagnostics Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Access comprehensive system diagnostics through the interactive web interface:

- **URL** http://localhost:8000/diagnostics
- **Features** Real-time system health information and performance analysis

**Connection Speed Test**

- Raw asyncpg connection performance testing
- Direct database connectivity validation

**Connection Performance**

- Comprehensive connection scenarios (raw asyncpg, SQLAlchemy engine, pool behavior, DNS resolution)
- Connection pool analysis and performance metrics

**Schema Health Check**

- Table sizes and row counts
- Index usage statistics and performance metrics
- Potential missing indexes for tables with sequential scans
- Unused indexes identification
- Table statistics and dead tuple analysis

**Performance & Locks**

- Deadlock statistics and trends
- Currently locked tables (public schema only)
- Top active queries with duration and wait events
- Long running queries (>30s) identification

Pipeline Reporting Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Access daily pipeline metrics and performance analytics:

- **URL** http://localhost:8000/reporting
- **Features** Comprehensive pipeline performance analysis

**Pipeline Metrics**

- Daily aggregations of execution counts, error rates, and performance data
- Pipeline type filtering (e.g., extraction, audit, sales)
- Pipeline name filtering for specific pipeline analysis
- Time range filtering (last 1-30 days)

**Performance Analytics**

- Track throughput, duration, and DML operation trends
- Error rate monitoring with visual indicators (high, medium, low)
- Pagination for navigating large datasets with configurable page sizes
- Auto-refresh with materialized view refreshes automatically on page load
- Real-time data built on PostgreSQL materialized views for fast query performance

Alerting Configuration
-----------------------

Slack Integration
~~~~~~~~~~~~~~~~~

Configure Slack alerts for monitoring:

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Create new app for your workspace
   - Add Incoming Webhooks feature

2. **Get Webhook URL**
   - Create webhook for your channel
   - Copy the webhook URL

3. **Configure Environment**

   .. code-block:: bash

      SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

Alert Types
~~~~~~~~~~~

**Celery Queue Alerts**

- Queue depth exceeds thresholds (WARNING: 50+, CRITICAL: 100+)
- Worker status and task processing issues

**Anomaly Detection Alerts**

- Statistical anomalies detected in pipeline executions
- Metric threshold violations (duration, rows, throughput, DML operations)
- Z-score analysis results

**Timeliness & Freshness Alerts**

- Pipeline execution timeliness failures
- DML operation freshness violations
- Overdue pipeline executions

Monitoring Strategy
-------------------

Scheduled Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up regular monitoring checks:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests
         import schedule
         import time

         def check_freshness():
             response = requests.post("http://localhost:8000/freshness")
             print(f"Freshness check: {response.status_code}")

         def check_timeliness():
             response = requests.post(
                 "http://localhost:8000/timeliness",
                 json={"lookback_minutes": 60}
             )
             print(f"Timeliness check: {response.status_code}")

         def monitor_celery_queue():
             response = requests.post("http://localhost:8000/celery/monitor-queue")
             print(f"Celery queue check: {response.status_code}")

         def cleanup_logs():
             response = requests.post(
                 "http://localhost:8000/log_cleanup",
                 json={"retention_days": 365}
             )
             print(f"Log cleanup: {response.status_code}")

         # Schedule tasks
         schedule.every(5).minutes.do(check_freshness)
         schedule.every(5).minutes.do(check_timeliness)
         schedule.every(5).minutes.do(monitor_celery_queue)
         schedule.every().day.at("02:00").do(cleanup_logs)

         while True:
             schedule.run_pending()
             time.sleep(60)

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx
         import schedule
         import time

         def check_freshness():
             with httpx.Client() as client:
                 response = client.post("http://localhost:8000/freshness")
                 print(f"Freshness check: {response.status_code}")

         def check_timeliness():
             with httpx.Client() as client:
                 response = client.post(
                     "http://localhost:8000/timeliness",
                     json={"lookback_minutes": 60}
                 )
                 print(f"Timeliness check: {response.status_code}")

         def monitor_celery_queue():
             with httpx.Client() as client:
                 response = client.post("http://localhost:8000/celery/monitor-queue")
                 print(f"Celery queue check: {response.status_code}")

         def cleanup_logs():
             with httpx.Client() as client:
                 response = client.post(
                     "http://localhost:8000/log_cleanup",
                     json={"retention_days": 365}
                 )
                 print(f"Log cleanup: {response.status_code}")

         # Schedule tasks
         schedule.every(5).minutes.do(check_freshness)
         schedule.every(5).minutes.do(check_timeliness)
         schedule.every(5).minutes.do(monitor_celery_queue)
         schedule.every().day.at("02:00").do(cleanup_logs)

         while True:
             schedule.run_pending()
             time.sleep(60)

   .. tab:: curl

      .. code-block:: bash

         # Add to crontab
         # Check freshness every 5 minutes
         */5 * * * * curl -X POST "http://localhost:8000/freshness"
         
         # Check timeliness every 5 minutes
         */5 * * * * curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
         
         # Monitor Celery queue every 5 minutes
         */5 * * * * curl -X POST "http://localhost:8000/celery/monitor-queue"
         
         # Clean up logs daily (365 days retention)
         0 2 * * * curl -X POST "http://localhost:8000/log_cleanup" -H "Content-Type: application/json" -d '{"retention_days": 365}'

   .. tab:: HTTPie

      .. code-block:: bash

         # Add to crontab
         # Check freshness every 5 minutes
         */5 * * * * http POST localhost:8000/freshness
         
         # Check timeliness every 5 minutes
         */5 * * * * http POST localhost:8000/timeliness lookback_minutes=60
         
         # Monitor Celery queue every 5 minutes
         */5 * * * * http POST localhost:8000/celery/monitor-queue
         
         # Clean up logs daily (365 days retention)
         0 2 * * * http POST localhost:8000/log_cleanup retention_days=365

Monitoring Frequency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recommended monitoring frequencies:

- **Freshness** Every 5 minutes
- **Timeliness** Every 5 minutes
- **Queue Monitoring** Every 5 minutes
- **Log Cleanup** Daily, Weekly, or Monthly

Load Testing
------------

Trigger Load Tests
~~~~~~~~~~~~~~~~~~

Use Locust for load testing:

.. code-block:: bash

   # Run load tests using Makefile
   make load-test
   
   # Web interface: http://localhost:8089

Load Test Scenarios
~~~~~~~~~~~~~~~~~~~

**Pipeline Execution Users** (998 users):

- Create and execute pipelines
- 5-minute execution times
- 1% anomaly generation rate

**Monitoring Users** (1 user):

- Run freshness and timeliness checks
- 5-minute monitoring intervals

**Heartbeat Users** (1 user):

- Health check endpoint (http://localhost:8000)
- 1-minute intervals

Performance Targets
~~~~~~~~~~~~~~~~~~~

Based on the load test configuration, the system should handle:

- **998 concurrent pipelines** executing every 5 minutes
- **~10-20 RPS** sustained load (998 users ÷ 300 seconds)
- **Sub-second response times** for all endpoints
- **<1% failure rate** under normal conditions
- **Continuous monitoring** with dedicated monitoring and heartbeat users
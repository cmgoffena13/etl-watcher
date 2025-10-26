Monitoring & Health Checks
============================

This guide covers how to set up comprehensive monitoring for your Watcher instance.
Watcher provides multiple monitoring capabilities to ensure your data pipelines are running optimally:

- **Freshness Monitoring**: Track data staleness and DML operations
- **Timeliness Monitoring**: Validate pipeline execution timing
- **Queue Monitoring**: Track Celery task queue depth and performance

Freshness Monitoring
--------------------

Purpose
~~~~~~~

Freshness monitoring tracks when data was last modified to detect stale data:

- **DML Operations**: Monitors inserts, updates, and soft deletes
- **Staleness Detection**: Identifies data that hasn't had DML activity recently
- **Alerting**: Notifies when data becomes stale

Configuration
~~~~~~~~~~~~~

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

   .. tab:: Python

      .. code-block:: python

         import httpx

         response = httpx.post("http://localhost:8000/freshness")
         print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/freshness"

   .. tab:: Go

      .. code-block:: go

         package main

         import (
             "encoding/json"
             "fmt"
             "net/http"
         )

         func main() {
             resp, _ := http.Post("http://localhost:8000/freshness", 
                 "application/json", nil)
             defer resp.Body.Close()
             
             var result map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&result)
             fmt.Println(result)
         }

   .. tab:: Scala

      .. code-block:: scala

         import java.net.http.{HttpClient, HttpRequest, HttpResponse}
         import java.net.URI

         object FreshnessExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/freshness"))
                     .POST(HttpRequest.BodyPublishers.noBody())
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

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

   .. tab:: Python

      .. code-block:: python

         import httpx

         response = httpx.post(
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

   .. tab:: Go

      .. code-block:: go

         package main

         import (
             "bytes"
             "encoding/json"
             "fmt"
             "net/http"
         )

         type TimelinessRequest struct {
             LookbackMinutes int `json:"lookback_minutes"`
         }

         func main() {
             data := TimelinessRequest{
                 LookbackMinutes: 60,
             }
             
             jsonData, _ := json.Marshal(data)
             resp, _ := http.Post("http://localhost:8000/timeliness", 
                 "application/json", bytes.NewBuffer(jsonData))
             defer resp.Body.Close()
             
             var result map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&result)
             fmt.Println(result)
         }

   .. tab:: Scala

      .. code-block:: scala

         import java.net.http.{HttpClient, HttpRequest, HttpResponse}
         import java.net.URI
         import play.api.libs.json.Json

         object TimelinessExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val json = Json.obj(
                     "lookback_minutes" -> 60
                 ).toString()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/timeliness"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(json))
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

**Response:**

.. code-block:: json

   {
     "status": "queued"
   }

**Lookback Period** How far back to look for executions (in minutes)

Celery Queue Monitoring
-----------------------

Monitor Celery queue health and performance with detailed task breakdown:

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         response = httpx.post("http://localhost:8000/celery/monitor-queue")
         print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/celery/monitor-queue"

   .. tab:: Go

      .. code-block:: go

         package main

         import (
             "encoding/json"
             "fmt"
             "net/http"
         )

         func main() {
             resp, _ := http.Post("http://localhost:8000/celery/monitor-queue", 
                 "application/json", nil)
             defer resp.Body.Close()
             
             var result map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&result)
             fmt.Println(result)
         }

   .. tab:: Scala

      .. code-block:: scala

         import java.net.http.{HttpClient, HttpRequest, HttpResponse}
         import java.net.URI

         object QueueMonitoringExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/celery/monitor-queue"))
                     .POST(HttpRequest.BodyPublishers.noBody())
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

**Response:**

.. code-block:: json

   {
     "status": "success",
     "total_pending": 2855,
     "regular_queue_pending": 2855,
     "scheduled_queue_pending": 0,
     "beat_scheduled_tasks": 0,
     "task_breakdown_formatted": [
       "Detect Anomalies Task: 1375",
       "Pipeline Execution Closure Maintain: 1477",
       "Timeliness Check Task: 3"
     ],
     "task_breakdown_raw": {
       "detect_anomalies_task": 1375,
       "timeliness_check_task": 3,
       "freshness_check_task": 0,
       "address_lineage_closure_rebuild_task": 0,
       "pipeline_execution_closure_maintain_task": 1477,
       "unknown": 0
     }
   }

Alert Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default alert thresholds for Celery queue monitoring:

- **INFO** (20+ messages): Queue building up
- **WARNING** (50+ messages): Queue getting backed up
- **CRITICAL** (100+ messages): Queue severely backed up

Scheduled Monitoring Tasks
---------------------------

Watcher includes built-in scheduled monitoring tasks that run automatically:

**Celery Beat Scheduler**

- **Freshness Check**: Runs every hour (configurable)
- **Timeliness Check**: Runs every 15 minutes (configurable)  
- **Queue Health Check**: Runs every 5 minutes (configurable)

**Configuration**

Set cron schedules and monitoring parameters via environment variables:

.. code-block:: bash

   # Freshness check schedule (default: every hour)
   WATCHER_FRESHNESS_CHECK_SCHEDULE="0 * * * *"
   
   # Timeliness check schedule (default: every 15 minutes)
   WATCHER_TIMELINESS_CHECK_SCHEDULE="*/15 * * * *"
   
   # Queue health check schedule (default: every 5 minutes)
   WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE="*/5 * * * *"
   
   # Timeliness check lookback period (default: 60 minutes)
   WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES=60

**Queue Separation**

- **Regular Queue** (`celery`): Pipeline execution and processing tasks
- **Scheduled Queue** (`scheduled`): Monitoring and health check tasks

This separation prevents monitoring tasks from being delayed by heavy pipeline workloads.

**Important Configuration Notes**

- **Timeliness Lookback Period**: The default 60-minute lookback period works for most pipelines. If your pipelines typically run longer than 1 hour, increase `WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES` to ensure timeliness checks can properly evaluate long-running executions.

  .. code-block:: bash

     # For pipelines that run up to 3 hours
     WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES=180
     
     # For pipelines that run up to 6 hours  
     WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES=360

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

**Queue Analysis**

- Detailed breakdown of queued tasks by type
- Task counts and percentage distribution
- Identification of task types dominating the queue
- Real-time queue composition analysis

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

.. code-block:: text

   🚨 CRITICAL
   Celery Queue Alert
   Timestamp: 2025-10-25 23:42:22 UTC
   Message: Queue has 2939 pending tasks
   
   Details:
   • Total pending: 2939
   • Regular queue: 2939
   • Scheduled queue: 0
   • Beat scheduled tasks: 0
   • Task breakdown: ['Detect Anomalies Task: 1420', 'Timeliness Check Task: 3', 'Freshness Check Task: 3', 'Pipeline Execution Closure Maintain Task: 1513']

**Anomaly Detection Alerts**

- Statistical anomalies detected in pipeline executions
- Metric threshold violations (duration, rows, throughput, DML operations)
- Z-score analysis results

.. code-block:: text

   ⚠️ WARNING
   Anomaly Detection
   Timestamp: 2025-01-09 20:30:45 UTC
   Message: Anomalies Detected for Pipeline 'analytics_pipeline' (ID: 123) - Execution ID 21 flagged
   
   Details:
   • Total Anomalies: 2
   • Metrics: ['duration_seconds', 'throughput']
   • Anomalies: 
   	• duration_seconds: 4914 (Range: 0 - 4767)
   	• throughput: 271.96 (Range: 0 - 250)

**Timeliness & Freshness Alerts**

- Pipeline execution timeliness failures
- DML operation freshness violations
- Overdue pipeline executions

**Timeliness Alert Example**

.. code-block:: text

   ⚠️ WARNING
   Timeliness Check - Pipeline Execution
   Timestamp: 2025-09-28 17:24:41 UTC
   Message: Pipeline Execution Timeliness Check - 2 new execution(s) overdue
   
   Details:
   • Failed Executions:
       • Pipeline 'hourly_pipeline_066' (Execution ID: 8842): 28.72 minutes (running), Expected within 15 minutes (child config)
       • Pipeline 'hourly_pipeline_701' (Execution ID: 8843): 28.72 minutes (running), Expected within 15 minutes (child config)

**Freshness Alert Example**

.. code-block:: text

   ⚠️ WARNING
   Freshness Check - Pipeline DML
   Timestamp: 2025-09-30 00:34:13 UTC
   Message: Pipeline Freshness Check - 2 NEW pipeline(s) overdue
   
   Details:
   • Failed Pipelines:
       • hourly_pipeline_037 (ID: 30): Last DML 2025-09-28 17:34:20.019491+00:00, Expected within 6 hours
       • hourly_pipeline_057 (ID: 49): Last DML 2025-09-28 17:34:41.016885+00:00, Expected within 6 hours

Monitoring Strategy
-------------------

Automated Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watcher includes built-in scheduled monitoring that runs automatically via Celery Beat:

**Automatic Monitoring Tasks**

- **Freshness Checks**: Every hour (configurable)
- **Timeliness Checks**: Every 15 minutes (configurable)
- **Celery Queue Health Checks**: Every 5 minutes (configurable)

**Note**: Log cleanup is not included in automatic monitoring and should be scheduled separately based on your data retention needs. See the `Log Cleanup & Maintenance <log_cleanup.html>`_ guide for detailed configuration options.

**Manual Monitoring** (Optional)

For additional monitoring or custom schedules, you can still trigger checks manually:

.. code-block:: bash

   # Manual freshness check
   curl -X POST "http://localhost:8000/freshness"
   
   # Manual timeliness check
   curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
   
   # Manual queue monitoring
   curl -X POST "http://localhost:8000/celery/monitor-queue"
   
   # Log cleanup (run as needed)
   curl -X POST "http://localhost:8000/log_cleanup" -H "Content-Type: application/json" -d '{"retention_days": 365}'

Monitoring Frequency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Default Automated Frequencies:**

- **Freshness** Every hour
- **Timeliness** Every 15 minutes  
- **Queue Monitoring** Every 5 minutes

**Customization:**

Configure different schedules via environment variables:

.. code-block:: bash

   # More frequent monitoring
   WATCHER_FRESHNESS_CHECK_SCHEDULE="*/30 * * * *"    # Every 30 minutes
   WATCHER_TIMELINESS_CHECK_SCHEDULE="*/5 * * * *"    # Every 5 minutes
   WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE="*/2 * * * *"  # Every 2 minutes

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

**Pipeline Execution Users** (999 users):

- Create and execute pipelines
- 5-minute execution times
- 1% anomaly generation rate

**Heartbeat Users** (1 user):

- Health check endpoint (http://localhost:8000)
- 1-minute intervals

**Note**: Monitoring tasks (freshness, timeliness, queue health) now run automatically via scheduled Celery Beat tasks, so they're no longer included in load testing.

Performance Targets
~~~~~~~~~~~~~~~~~~~

Based on the load test configuration, the system should handle:

- **999 concurrent pipelines** executing every 5 minutes
- **~10-20 RPS** sustained load (999 users ÷ 300 seconds)
- **Sub-second response times** for all endpoints
- **<1% failure rate** under normal conditions
- **Automated monitoring** via Celery Beat scheduler (separate from load testing)
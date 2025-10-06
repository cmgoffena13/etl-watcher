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

Queue Monitoring
----------------

Celery Queue Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Celery queue health and performance:

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

.. code-block:: text

   🚨 CRITICAL
   Celery Queue Alert
   Timestamp: 2025-09-28 06:04:26 UTC
   Message: Queue has 2367 pending tasks
   
   Details:
   • Messages in queue: 2367
   • Scheduled tasks: 0
   • Total pending: 2367

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

Scheduled Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up regular monitoring checks using cron jobs or an orchestrator/scheduler:

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
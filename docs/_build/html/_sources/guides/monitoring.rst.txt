Monitoring & Health Checks
============================

This guide covers how to set up comprehensive monitoring for your Watcher instance.

Overview
--------

Watcher provides multiple monitoring capabilities to ensure your data pipelines are running optimally:

- **Freshness Monitoring** Track data staleness and DML operations
- **Timeliness Monitoring** Validate pipeline execution timing
- **System Health** Monitor database, Redis, and Celery health
- **Queue Monitoring** Track Celery task queue depth and performance

Freshness Monitoring
--------------------

Purpose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Freshness monitoring tracks when data was last modified to detect stale data:

- **DML Operations** Monitors inserts, updates, and soft deletes
- **Staleness Detection** Identifies data that hasn't been updated recently
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

- **freshness_number** Time threshold (e.g., 24)
- **freshness_datepart** Time unit (hour, day, week, month, quarter, year)
- **mute_freshness_check** Disable freshness monitoring

Supported Time Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **hour** Monitor hourly freshness
- **day** Monitor daily freshness
- **week** Monitor weekly freshness
- **month** Monitor monthly freshness
- **quarter** Monitor quarterly freshness
- **year** Monitor yearly freshness

Running Freshness Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trigger freshness checks manually:

.. code-block:: bash

   curl -X POST "http://localhost:8000/freshness"
   
   # Response
   {
     "status": "queued"
   }

The check runs as a background Celery task and monitors all configured pipelines.

Timeliness Monitoring
---------------------

Purpose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timeliness monitoring validates that pipeline executions complete within expected timeframes:

- **Execution Timing** Tracks how long pipelines take to complete
- **Threshold Validation** Compares against configured timeliness thresholds
- **Performance Issues** Identifies slow or stuck pipelines

Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. code-block:: bash

   curl -X POST "http://localhost:8000/timeliness" \
        -H "Content-Type: application/json" \
        -d '{
          "lookback_minutes": 60
        }'
   
   # Response
   {
     "status": "queued"
   }

**Lookback Period** How far back to look for executions (in minutes)

System Health Monitoring
------------------------

Diagnostics Page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Access comprehensive system diagnostics:

- **URL** http://localhost:8000/diagnostics
- **Features** Real-time system health information
- **Sections** Database, Redis, Celery, Performance metrics

Database Health
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor database connectivity and performance:

- **Connection Status** Database connectivity
- **Query Performance** Slow query detection
- **Schema Health** Database schema validation
- **Index Usage** Index utilization metrics

Redis Health
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Redis connectivity and performance:

- **Connection Status** Redis connectivity
- **Memory Usage** Redis memory consumption
- **Key Count** Number of keys in Redis
- **Performance** Redis operation latency

Celery Health
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Celery workers and queues:

- **Worker Status** Active workers and their status
- **Queue Depth** Number of pending tasks
- **Task Performance** Task execution metrics
- **Error Rates** Failed task percentages

Queue Monitoring
----------------

Celery Queue Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Celery queue health and performance:

.. code-block:: bash

   curl -X POST "http://localhost:8000/celery/monitor-queue"
   
   # Response
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
   • Workers active: 2
   • Queue: celery

Performance Monitoring
----------------------

Connection Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor database connection performance:

- **URL** http://localhost:8000/diagnostics/connection-performance
- **Metrics** Connection times, query performance
- **Alerts** Slow query detection

Schema Health
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor database schema health:

- **URL** http://localhost:8000/diagnostics/schema-health
- **Validation** Schema integrity checks
- **Indexes** Index usage and performance

Performance Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor application performance:

- **URL** http://localhost:8000/diagnostics/performance
- **Metrics** Request/response times, error rates
- **Trends** Performance over time

Celery Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor Celery performance:

- **URL** http://localhost:8000/diagnostics/celery
- **Workers** Worker status and activity
- **Tasks** Task performance and execution times
- **Queues** Queue depth and processing rates

Alerting Configuration
-----------------------

Slack Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

      export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
      
      # Restart application
      uv run python src/app.py

Alert Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Queue Alerts**
- Queue depth exceeds thresholds
- Worker status issues
- Task processing delays

**Anomaly Alerts**
- Statistical anomalies detected
- Metric threshold violations
- Performance degradation

**System Alerts**
- Database connectivity issues
- Redis connectivity issues
- Application errors

Monitoring Strategy
-------------------

Scheduled Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up regular monitoring checks:

.. code-block:: bash

   # Add to crontab
   # Check freshness every hour
   0 * * * * curl -X POST "http://localhost:8000/freshness"
   
   # Check timeliness every 30 minutes
   */30 * * * * curl -X POST "http://localhost:8000/timeliness" -H "Content-Type: application/json" -d '{"lookback_minutes": 60}'
   
   # Monitor Celery queue every 5 minutes
   */5 * * * * curl -X POST "http://localhost:8000/celery/monitor-queue"
   
   # Clean up logs daily
   0 2 * * * curl -X POST "http://localhost:8000/log_cleanup"

Monitoring Frequency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recommended monitoring frequencies:

- **Freshness** Every hour
- **Timeliness** Every 30 minutes
- **Queue Monitoring** Every 5 minutes
- **Log Cleanup** Daily
- **System Diagnostics** As needed

Load Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Locust for load testing:

.. code-block:: bash

   # Install Locust
   pip install locust
   
   # Run load tests
   locust -f src/diagnostics/locustfile.py --host=http://localhost:8000
   
   # Web interface: http://localhost:8089

Load Test Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline Execution Users** (998 users):
- Create and execute pipelines
- 5-minute execution times
- 1% anomaly generation rate

**Monitoring Users** (1 user):
- Run freshness and timeliness checks
- 5-minute monitoring intervals

**Heartbeat Users** (1 user):
- Health check endpoints
- 1-minute intervals

Performance Targets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Response Time** < 200ms for API endpoints
- **Throughput** > 1000 requests/second
- **Error Rate** < 0.1%
- **Queue Depth** < 50 messages
- **Worker Utilization** 70-80%

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Freshness Alerts**
- Check data modification timestamps
- Verify freshness thresholds
- Review data pipeline schedules

**Timeliness Alerts**
- Check pipeline execution times
- Verify timeliness thresholds
- Review system performance

**Queue Alerts**
- Check Celery worker status
- Verify Redis connectivity
- Review task processing rates

**System Alerts**
- Check database connectivity
- Verify Redis connectivity
- Review application logs

Performance Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Slow Responses**
- Check database performance
- Review query optimization
- Verify connection pooling

**High Queue Depth**
- Scale Celery workers
- Check task processing rates
- Review rate limiting

**Memory Issues**
- Monitor memory usage
- Check for memory leaks
- Review worker configuration

Best Practices
--------------

Monitoring Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Comprehensive Coverage** Monitor all critical components
- **Appropriate Thresholds** Set realistic alert thresholds
- **Regular Review** Review monitoring results regularly
- **Alert Fatigue** Avoid overly sensitive alerts

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Database Optimization** Optimize queries and indexes
- **Connection Pooling** Tune connection pool settings
- **Worker Scaling** Scale workers based on load
- **Caching** Implement appropriate caching strategies

Alert Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Clear Alerts** Use descriptive alert messages
- **Actionable Alerts** Include remediation steps
- **Alert Escalation** Implement alert escalation procedures
- **Alert History** Track alert trends and patterns

Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Regular Cleanup** Clean up old logs and data
- **Performance Tuning** Regular performance optimization
- **Security Updates** Keep dependencies updated
- **Backup Strategy** Implement data backup procedures

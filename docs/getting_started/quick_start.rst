Quick Start Guide
=================

This guide will get you up and running with Watcher in under 10 minutes.

Step 1: Create Your First Pipeline
----------------------------------

1. **Create a pipeline type**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/pipeline_type" \
           -H "Content-Type: application/json" \
           -d '{
             "name": "extraction",
             "group_name": "databricks"
           }'

2. **Create a pipeline**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/pipeline" \
           -H "Content-Type: application/json" \
           -d '{
             "name": "My Data Pipeline",
             "pipeline_type_name": "extraction",
             "next_watermark": "2024-01-01T00:00:00Z"
           }'

Step 2: Start Pipeline Execution
-------------------------------

1. **Start an execution**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/start_pipeline_execution" \
           -H "Content-Type: application/json" \
           -d '{
             "pipeline_id": 1,
             "start_date": "2024-01-01T10:00:00Z",
             "full_load": true,
             "watermark": "2024-01-01T00:00:00Z",
             "next_watermark": "2024-01-01T23:59:59Z"
           }'

2. **End the execution with metrics**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/end_pipeline_execution" \
           -H "Content-Type: application/json" \
           -d '{
             "id": 1,
             "end_date": "2024-01-01T10:05:00Z",
             "completed_successfully": true,
             "total_rows": 1000,
             "inserts": 800,
             "updates": 200,
             "soft_deletes": 0
           }'

Step 3: Set Up Monitoring
-------------------------

1. **Create an address for monitoring**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/address" \
           -H "Content-Type: application/json" \
           -d '{
             "name": "my_table",
             "address_type_name": "databricks",
             "address_type_group_name": "database"
           }'

2. **Run a freshness check**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/freshness"

3. **Run a timeliness check**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/timeliness" \
           -H "Content-Type: application/json" \
           -d '{
             "lookback_minutes": 60
           }'

Step 4: Configure Anomaly Detection
-----------------------------------

1. **Create an anomaly detection rule**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/anomaly_detection_rule" \
           -H "Content-Type: application/json" \
           -d '{
             "pipeline_id": 1,
             "metric_field": "total_rows",
             "z_threshold": 2.0,
             "minimum_executions": 5
           }'

2. **Anomaly detection runs automatically** after each successful pipeline execution

Step 5: Monitor Your System
--------------------------

1. **Check system health**

   Visit: http://localhost:8000/diagnostics

2. **View API documentation**

   Visit: http://localhost:8000/scalar

3. **Monitor Celery queue**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/celery/monitor-queue"

Next Steps
----------

- **Set up scheduled monitoring** Configure cron jobs to ping the monitoring endpoints
- **Configure Slack alerts** Add your Slack webhook URL for notifications
- **Set up anomaly detection rules** Create rules for your specific metrics
- **Explore the diagnostics page** Monitor system health and performance

Common Issues
-------------

**Port already in use**
   Make sure ports 8000, 5432, and 6379 are available

**Database connection failed**
   Ensure PostgreSQL is running and accessible

**Redis connection failed**
   Ensure Redis is running and accessible

**Migration errors**
   Check that the database exists and you have proper permissions

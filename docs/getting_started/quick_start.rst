Quick Start Guide
=================

This guide will get you up and running with Watcher.

Step 1: Create Your First Pipeline
----------------------------------

1. **Create a pipeline** (automatically creates pipeline type if needed)

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/pipeline", json={
                "name": "My Data Pipeline",
                "pipeline_type_name": "extraction"
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/pipeline", json={
                "name": "My Data Pipeline",
                "pipeline_type_name": "extraction"
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/pipeline" \
                 -H "Content-Type: application/json" \
                 -d '{"name": "My Data Pipeline", "pipeline_type_name": "extraction"}'

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/pipeline \
                 name="My Data Pipeline" \
                 pipeline_type_name=extraction

Step 2: Start Pipeline Execution
-------------------------------

2. **Start an execution**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/start_pipeline_execution", json={
                "pipeline_id": 1,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": True,
                "watermark": "2024-01-01T00:00:00Z",
                "next_watermark": "2024-01-01T23:59:59Z"
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/start_pipeline_execution", json={
                "pipeline_id": 1,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": True,
                "watermark": "2024-01-01T00:00:00Z",
                "next_watermark": "2024-01-01T23:59:59Z"
            })
            print(response.json())

      .. tab:: curl

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

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/start_pipeline_execution \
                 pipeline_id=1 \
                 start_date="2024-01-01T10:00:00Z" \
                 full_load=true \
                 watermark="2024-01-01T00:00:00Z" \
                 next_watermark="2024-01-01T23:59:59Z"

3. **End the execution with metrics**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/end_pipeline_execution", json={
                "id": 1,
                "end_date": "2024-01-01T10:05:00Z",
                "completed_successfully": True,
                "total_rows": 1000,
                "inserts": 800,
                "updates": 200,
                "soft_deletes": 0
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/end_pipeline_execution", json={
                "id": 1,
                "end_date": "2024-01-01T10:05:00Z",
                "completed_successfully": True,
                "total_rows": 1000,
                "inserts": 800,
                "updates": 200,
                "soft_deletes": 0
            })
            print(response.json())

      .. tab:: curl

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

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/end_pipeline_execution \
                 id=1 \
                 end_date="2024-01-01T10:05:00Z" \
                 completed_successfully=true \
                 total_rows=1000 \
                 inserts=800 \
                 updates=200 \
                 soft_deletes=0

Step 3: Set Up Monitoring
-------------------------

1. **Create data lineage** (automatically creates addresses and address types if needed)

   .. note::
      Set ``WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true`` to automatically create anomaly detection rules for new pipelines.

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/address_lineage", json={
                "pipeline_id": 1,
                "source_addresses": [
                    {
                        "name": "source_table",
                        "address_type_name": "databricks",
                        "address_type_group_name": "database"
                    }
                ],
                "target_addresses": [
                    {
                        "name": "target_table",
                        "address_type_name": "databricks",
                        "address_type_group_name": "database"
                    }
                ]
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/address_lineage", json={
                "pipeline_id": 1,
                "source_addresses": [
                    {
                        "name": "source_table",
                        "address_type_name": "databricks",
                        "address_type_group_name": "database"
                    }
                ],
                "target_addresses": [
                    {
                        "name": "target_table",
                        "address_type_name": "databricks",
                        "address_type_group_name": "database"
                    }
                ]
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/address_lineage" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "source_addresses": [
                     {
                       "name": "source_table",
                       "address_type_name": "databricks",
                       "address_type_group_name": "database"
                     }
                   ],
                   "target_addresses": [
                     {
                       "name": "target_table",
                       "address_type_name": "databricks",
                       "address_type_group_name": "database"
                     }
                   ]
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/address_lineage \
                 pipeline_id=1 \
                 source_addresses:='[{"name": "source_table", "address_type_name": "databricks", "address_type_group_name": "database"}]' \
                 target_addresses:='[{"name": "target_table", "address_type_name": "databricks", "address_type_group_name": "database"}]'

2. **Run a freshness check**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/freshness")
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/freshness")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/freshness"

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/freshness

3. **Run a timeliness check**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/timeliness", json={
                "lookback_minutes": 60
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/timeliness", json={
                "lookback_minutes": 60
            })
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

Step 4: Run a Celery Queue Check
--------------------------------

1. **Monitor Celery queue**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/celery/monitor-queue")
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/celery/monitor-queue")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/celery/monitor-queue"

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/celery/monitor-queue

Step 5: Configure Anomaly Detection
-----------------------------------

1. **Create an anomaly detection rule**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests
            
            response = requests.post("http://localhost:8000/anomaly_detection_rule", json={
                "pipeline_id": 1,
                "metric_field": "total_rows",
                "z_threshold": 2.0,
                "minimum_executions": 5
            })
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/anomaly_detection_rule", json={
                "pipeline_id": 1,
                "metric_field": "total_rows",
                "z_threshold": 2.0,
                "minimum_executions": 5
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "total_rows",
                   "z_threshold": 2.0,
                   "minimum_executions": 5
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/anomaly_detection_rule \
                 pipeline_id=1 \
                 metric_field=total_rows \
                 z_threshold=2.0 \
                 minimum_executions=5

2. **Anomaly detection runs automatically** after each successful pipeline execution

Step 6: Monitor Your System
--------------------------

1. **Check system health**

   Visit: http://localhost:8000/diagnostics

2. **View API documentation**

   Visit: http://localhost:8000/scalar

Next Steps
----------

- **Set up scheduled monitoring** Configure cron jobs to ping the monitoring endpoints
- **Configure Slack alerts** Add your Slack webhook URL for notifications
- **Set up anomaly detection rules** Create rules for your specific metrics
- **Explore the diagnostics page** Monitor system health and performance

Common Issues
-------------

**Port already in use**
   Make sure port 8000 is available on your host machine

**Docker containers not starting**
   Check that Docker and Docker Compose are running properly

**Database connection failed**
   Ensure the PostgreSQL container is running: ``docker-compose ps``

**Redis connection failed**
   Ensure the Redis container is running: ``docker-compose ps``

**Migration errors**
   Try restarting the application container: ``docker-compose restart app``

Anomaly Detection
=================

This guide covers how to set up and use anomaly detection in Watcher.
Watcher's anomaly detection system uses statistical analysis to identify unusual patterns 
in pipeline execution metrics. It automatically runs after each successful pipeline execution 
and can detect anomalies in various metrics like execution time, row counts, and throughput.

How It Works
------------

Statistical Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The anomaly detection system uses z-score analysis:

1. **Baseline Calculation** Analyzes historical execution data
2. **Statistical Metrics** Calculates mean and standard deviation
3. **Z-Score Calculation** Determines how many standard deviations a value is from the mean
4. **Threshold Comparison** Compares z-score against configured threshold
5. **Anomaly Detection** Flags values that exceed the threshold

.. note::
   The system only compares executions that occurred during the same hour of day (e.g., 2 PM vs 2 PM) 
   to account for daily patterns, business hours, and data processing cycles. 
   This ensures more accurate anomaly detection by comparing like-with-like time periods.

Supported Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor various pipeline execution metrics:

- **total_rows** Total number of rows processed
- **duration_seconds** Execution duration in seconds
- **throughput** Rows processed per second
- **inserts** Number of insert operations
- **updates** Number of update operations
- **soft_deletes** Number of soft delete operations

Setting Up Anomaly Detection
----------------------------

Creating Detection Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   You can enable automatic creation of anomaly detection rules 
   by setting the ``WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES`` environment variable to 
   ``true``. This will automatically create all rules for a pipeline when it is created.

1. **Create an anomaly detection rule**

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            response = requests.post(
                "http://localhost:8000/anomaly_detection_rule",
                json={
                    "pipeline_id": 1,
                    "metric_field": "total_rows",
                    "z_threshold": 3.0,
                    "minimum_executions": 30
                }
            )
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            with httpx.Client() as client:
                response = client.post(
                    "http://localhost:8000/anomaly_detection_rule",
                    json={
                        "pipeline_id": 1,
                        "metric_field": "total_rows",
                        "z_threshold": 3.0,
                        "minimum_executions": 30
                    }
                )
                print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "total_rows",
                   "z_threshold": 3.0,
                   "minimum_executions": 30
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/anomaly_detection_rule \
                 pipeline_id=1 \
                 metric_field=total_rows \
                 z_threshold=3.0 \
                 minimum_executions=30

2. **Response**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.0,
        "minimum_executions": 5,
        "active": true,
        "created_at": "2024-01-01T10:00:00Z"
      }

Rule Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline ID** The pipeline to monitor for anomalies

**Metric Field** The specific metric to analyze:

- ``total_rows``: Monitor row count variations
- ``duration_seconds``: Monitor execution time variations
- ``throughput``: Monitor processing speed variations
- ``inserts``: Monitor insert operation variations
- ``updates``: Monitor update operation variations
- ``soft_deletes``: Monitor soft delete variations

**Z-Threshold** Sensitivity of anomaly detection:

- ``1.5``: Very sensitive (catches minor variations)
- ``2.0``: Standard sensitivity (recommended)
- ``2.5``: Less sensitive (catches major variations)
- ``3.0``: Very conservative (catches only extreme anomalies)

**Minimum Executions** Number of historical executions needed before analysis:

- ``5``: Minimum for basic analysis (would not recommend this)
- ``30``: Recommended for stable baselines

Multiple Rules
~~~~~~~~~~~~~~

Create multiple rules for comprehensive monitoring:

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            # Define rules to create
            rules = [
                {
                    "pipeline_id": 1,
                    "metric_field": "total_rows",
                    "z_threshold": 2.0,
                    "minimum_executions": 5
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "duration_seconds",
                    "z_threshold": 2.5,
                    "minimum_executions": 10
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "throughput",
                    "z_threshold": 1.8,
                    "minimum_executions": 8
                }
            ]

            # Create all rules
            for rule in rules:
                response = requests.post(
                    "http://localhost:8000/anomaly_detection_rule",
                    json=rule
                )
                print(f"{rule['metric_field']} rule:", response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            # Define rules to create
            rules = [
                {
                    "pipeline_id": 1,
                    "metric_field": "total_rows",
                    "z_threshold": 3.0,
                    "minimum_executions": 30
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "duration_seconds",
                    "z_threshold": 3.0,
                    "minimum_executions": 30
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "throughput",
                    "z_threshold": 3.0,
                    "minimum_executions": 30
                }
            ]

            # Create all rules
            with httpx.Client() as client:
                for rule in rules:
                    response = client.post(
                        "http://localhost:8000/anomaly_detection_rule",
                        json=rule
                    )
                    print(f"{rule['metric_field']} rule:", response.json())

      .. tab:: curl

         .. code-block:: bash

            # Monitor row count anomalies
            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "total_rows",
                   "z_threshold": 3.0,
                   "minimum_executions": 30
                 }'

            # Monitor execution time anomalies
            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "duration_seconds",
                   "z_threshold": 3.0,
                   "minimum_executions": 30
                 }'

            # Monitor throughput anomalies
            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "throughput",
                   "z_threshold": 3.0,
                   "minimum_executions": 30
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            # Monitor row count anomalies
            http POST localhost:8000/anomaly_detection_rule \
                 pipeline_id=1 \
                 metric_field=total_rows \
                 z_threshold=2.0 \
                 minimum_executions=5

            # Monitor execution time anomalies
            http POST localhost:8000/anomaly_detection_rule \
                 pipeline_id=1 \
                 metric_field=duration_seconds \
                 z_threshold=2.5 \
                 minimum_executions=10

            # Monitor throughput anomalies
            http POST localhost:8000/anomaly_detection_rule \
                 pipeline_id=1 \
                 metric_field=throughput \
                 z_threshold=1.8 \
                 minimum_executions=8

Automatic Execution
-------------------

Triggered Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Anomaly detection runs automatically after each successful pipeline execution:

1. **Pipeline execution completes successfully**
2. **System checks for active anomaly detection rules**
3. **For each rule, analyzes the execution metrics**
4. **Compares against historical baseline**
5. **Flags anomalies if detected**
6. **Sends alerts if anomalies are found**

No Manual Triggering Required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike monitoring checks, anomaly detection doesn't require manual triggering:

- **Automatic** Runs after every successful execution
- **Background** Processed by Celery workers
- **Real-time** Results available immediately
- **Persistent** Anomaly results stored in database

Anomaly Results
---------------

Understanding Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an anomaly is detected, the system stores detailed information:

.. code-block:: json

   {
     "pipeline_execution_id": 123,
     "rule_id": 1,
     "violation_value": 15000.0000,
     "z_score": 2.8000,
     "historical_mean": 8000.0000,
     "std_deviation_value": 2500.0000,
     "z_threshold": 2.0000,
     "threshold_min_value": 3000.0000,
     "threshold_max_value": 13000.0000,
     "context": {
       "lookback_days": 30,
       "minimum_executions": 30,
       "execution_count": 45
     },
     "detected_at": "2024-01-01T10:05:00Z"
   }

Result Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **violation_value** The actual metric value that triggered the anomaly
- **z_score** How many standard deviations from the mean
- **historical_mean** Average value from historical data
- **std_deviation_value** Standard deviation from historical data
- **z_threshold** Configured threshold for this rule
- **threshold_min_value** Minimum expected value
- **threshold_max_value** Maximum expected value

Alert Notifications
-------------------

Slack Alerts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When anomalies are detected, Slack alerts are sent automatically:

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

Alert Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure Slack webhooks for alerts:

.. code-block:: bash

   # Set Slack webhook URL
   SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

Managing Anomalies
------------------

Viewing Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all anomaly detection rules:

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            response = requests.get("http://localhost:8000/anomaly_detection_rule")
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            with httpx.Client() as client:
                response = client.get("http://localhost:8000/anomaly_detection_rule")
                print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X GET "http://localhost:8000/anomaly_detection_rule"

      .. tab:: HTTPie

         .. code-block:: bash

            http GET localhost:8000/anomaly_detection_rule

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "pipeline_id": 1,
          "metric_field": "total_rows",
          "z_threshold": 2.0,
          "minimum_executions": 5,
          "active": true,
          "created_at": "2024-01-01T10:00:00Z"
        }
      ]

Get specific rule details:

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            response = requests.get("http://localhost:8000/anomaly_detection_rule/1")
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            with httpx.Client() as client:
                response = client.get("http://localhost:8000/anomaly_detection_rule/1")
                print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X GET "http://localhost:8000/anomaly_detection_rule/1"

      .. tab:: HTTPie

         .. code-block:: bash

            http GET localhost:8000/anomaly_detection_rule/1

Updating Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update anomaly detection rules:

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            response = requests.patch(
                "http://localhost:8000/anomaly_detection_rule",
                json={
                    "id": 1,
                    "z_threshold": 2.5,
                    "minimum_executions": 10
                }
            )
            print(response.json())

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            with httpx.Client() as client:
                response = client.patch(
                    "http://localhost:8000/anomaly_detection_rule",
                    json={
                        "id": 1,
                        "z_threshold": 2.5,
                        "minimum_executions": 10
                    }
                )
                print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X PATCH "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "id": 1,
                   "z_threshold": 2.5,
                   "minimum_executions": 10
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            http PATCH localhost:8000/anomaly_detection_rule \
                 id=1 \
                 z_threshold=2.5 \
                 minimum_executions=10

Unflagging Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unflag anomalies that are false positives:

   .. tabs::

      .. tab:: Python - requests

         .. code-block:: python

            import requests

            response = requests.post(
                "http://localhost:8000/unflag_anomaly",
                json={
                    "pipeline_id": 1,
                    "pipeline_execution_id": 123,
                    "metric_field": ["total_rows", "duration_seconds"]
                }
            )
            print(response.status_code)

      .. tab:: Python - httpx

         .. code-block:: python

            import httpx

            with httpx.Client() as client:
                response = client.post(
                    "http://localhost:8000/unflag_anomaly",
                    json={
                        "pipeline_id": 1,
                        "pipeline_execution_id": 123,
                        "metric_field": ["total_rows", "duration_seconds"]
                    }
                )
                print(response.status_code)

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/unflag_anomaly" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "pipeline_execution_id": 123,
                   "metric_field": ["total_rows", "duration_seconds"]
                 }'

      .. tab:: HTTPie

         .. code-block:: bash

            http POST localhost:8000/unflag_anomaly \
                 pipeline_id=1 \
                 pipeline_execution_id=123 \
                 metric_field:='["total_rows", "duration_seconds"]'

This removes the anomaly flags and allows the execution to be included in future baseline calculations.

Best Practices
---------------

Rule Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Start Conservative** Begin with higher z-thresholds (2.5-3.0)
- **Adjust Based on Data** Lower thresholds as you understand your data patterns
- **Multiple Metrics** Monitor different aspects of pipeline performance
- **Sufficient History** Ensure enough historical data for stable baselines

Threshold Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A good rule of thumb is to start with a z-threshold of 3.0 and a minimum executions of 30. 
According to the Central Limit Theorem, 30 executions is enough to get a stable baseline for normal distrbution.

Monitoring Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Regular Review** Review anomaly results regularly
- **False Positive Management** Unflag false positives promptly
- **Threshold Tuning** Adjust thresholds based on results
- **Alert Fatigue** Avoid overly sensitive thresholds

Common Scenarios
----------------

Data Volume Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect unusual data volumes:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "total_rows",
     "z_threshold": 3.0,
     "minimum_executions": 30
   }

Performance Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect execution time issues:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "duration_seconds",
     "z_threshold": 3.0,
     "minimum_executions": 30
   }

Throughput Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect processing speed issues:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "throughput",
     "z_threshold": 3.0,
     "minimum_executions": 30
   }

DML Operation Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect unusual insert/update patterns:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "inserts",
     "z_threshold": 3.0,
     "minimum_executions": 30
   }

Advanced Configuration
----------------------

Auto-Creation Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable automatic rule creation for new pipelines:

.. code-block:: bash

   WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true

This automatically creates default anomaly detection rules for new pipelines.
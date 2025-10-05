Anomaly Detection
=================

This guide covers how to set up and use anomaly detection in Watcher.

Overview
--------

Watcher's anomaly detection system uses statistical analysis to identify unusual patterns in pipeline execution metrics. It automatically runs after each successful pipeline execution and can detect anomalies in various metrics like execution time, row counts, and throughput.

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
- ``5``: Minimum for basic analysis
- ``10``: Recommended for stable baselines
- ``20``: For highly variable pipelines

Multiple Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create multiple rules for comprehensive monitoring:

.. code-block:: bash

   # Monitor row count anomalies
   curl -X POST "http://localhost:8000/anomaly_detection_rule" \
        -H "Content-Type: application/json" \
        -d '{
          "pipeline_id": 1,
          "metric_field": "total_rows",
          "z_threshold": 2.0,
          "minimum_executions": 5
        }'

   # Monitor execution time anomalies
   curl -X POST "http://localhost:8000/anomaly_detection_rule" \
        -H "Content-Type: application/json" \
        -d '{
          "pipeline_id": 1,
          "metric_field": "duration_seconds",
          "z_threshold": 2.5,
          "minimum_executions": 10
        }'

   # Monitor throughput anomalies
   curl -X POST "http://localhost:8000/anomaly_detection_rule" \
        -H "Content-Type: application/json" \
        -d '{
          "pipeline_id": 1,
          "metric_field": "throughput",
          "z_threshold": 1.8,
          "minimum_executions": 8
        }'

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
     "rule_id": 1,
     "pipeline_execution_id": 123,
     "violation_value": 15000,
     "z_score": 2.8,
     "historical_mean": 8000,
     "std_deviation_value": 2500,
     "z_threshold": 2.0,
     "threshold_min_value": 3000,
     "threshold_max_value": 13000,
     "context": {
       "pipeline_name": "Daily Sales Pipeline",
       "execution_date": "2024-01-01T10:00:00Z"
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

   🚨 Anomalies Detected for Pipeline 'Daily Sales Pipeline' (ID: 1) - Execution ID 123 flagged
   
   Total Anomalies: 2
   
   Metrics:
   • total_rows: 15000 (z-score: 2.8, threshold: 2.0)
   • duration_seconds: 1800 (z-score: 2.3, threshold: 2.0)
   
   Anomalies:
   • total_rows: 15000 rows (expected: ~8000, z-score: 2.8)
   • duration_seconds: 1800 seconds (expected: ~1200, z-score: 2.3)

Alert Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure Slack webhooks for alerts:

.. code-block:: bash

   # Set Slack webhook URL
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
   
   # Restart application
   uv run python src/app.py

Managing Anomalies
------------------

Viewing Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all anomaly detection rules:

.. code-block:: bash

   curl -X GET "http://localhost:8000/anomaly_detection_rule"
   
   # Response
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

.. code-block:: bash

   curl -X GET "http://localhost:8000/anomaly_detection_rule/1"

Updating Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update anomaly detection rules:

.. code-block:: bash

   curl -X PATCH "http://localhost:8000/anomaly_detection_rule" \
        -H "Content-Type: application/json" \
        -d '{
          "id": 1,
          "z_threshold": 2.5,
          "minimum_executions": 10
        }'

Unflagging Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unflag anomalies that are false positives:

.. code-block:: bash

   curl -X POST "http://localhost:8000/unflag_anomaly" \
        -H "Content-Type: application/json" \
        -d '{
          "pipeline_id": 1,
          "pipeline_execution_id": 123,
          "metric_field": ["total_rows", "duration_seconds"]
        }'

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

**For Stable Pipelines**
- Z-threshold: 2.0-2.5
- Minimum executions: 10-15

**For Variable Pipelines**
- Z-threshold: 2.5-3.0
- Minimum executions: 15-20

**For Critical Pipelines**
- Z-threshold: 1.5-2.0
- Minimum executions: 5-10

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
     "z_threshold": 2.0,
     "minimum_executions": 5
   }

Performance Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect execution time issues:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "duration_seconds",
     "z_threshold": 2.5,
     "minimum_executions": 10
   }

Throughput Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect processing speed issues:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "throughput",
     "z_threshold": 1.8,
     "minimum_executions": 8
   }

DML Operation Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect unusual insert/update patterns:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "inserts",
     "z_threshold": 2.0,
     "minimum_executions": 5
   }

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**No Anomalies Detected**
- Check if rules are active
- Verify minimum executions requirement
- Check if z-threshold is too high

**Too Many False Positives**
- Increase z-threshold
- Increase minimum executions
- Review historical data quality

**Missing Alerts**
- Verify Slack webhook configuration
- Check Celery worker status
- Review alert delivery logs

**Baseline Issues**
- Ensure sufficient historical data
- Check for data quality issues
- Verify metric field selection

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Historical Data** More data = better baselines
- **Rule Complexity** Multiple rules increase processing time
- **Alert Volume** Too many alerts can cause fatigue
- **Storage** Anomaly results are stored in database

Advanced Configuration
----------------------

Auto-Creation Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable automatic rule creation for new pipelines:

.. code-block:: bash

   export WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true
   
   # Restart application
   uv run python src/app.py

This automatically creates default anomaly detection rules for new pipelines.

Custom Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For pipelines with known patterns, use custom thresholds:

.. code-block:: json

   {
     "pipeline_id": 1,
     "metric_field": "total_rows",
     "z_threshold": 1.5,
     "minimum_executions": 20
   }
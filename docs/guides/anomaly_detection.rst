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
   The system only compares successful executions that occurred during the same hour of day (e.g., 2 PM vs 2 PM) 
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

      .. tab:: Python

         .. code-block:: python

            import httpx

            response = httpx.post(
                "http://localhost:8000/anomaly_detection_rule",
                json={
                    "pipeline_id": 1,
                    "metric_field": "total_rows",
                    "z_threshold": 3.0,
                    "lookback_days": 30,
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
                   "lookback_days": 30,
                   "minimum_executions": 30
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

            type AnomalyRule struct {
                PipelineID        int     `json:"pipeline_id"`
                MetricField       string  `json:"metric_field"`
                ZThreshold        float64 `json:"z_threshold"`
                LookbackDays      int     `json:"lookback_days"`
                MinimumExecutions int     `json:"minimum_executions"`
            }

            func main() {
                data := AnomalyRule{
                    PipelineID:        1,
                    MetricField:       "total_rows",
                    ZThreshold:        3.0,
                    LookbackDays:      30,
                    MinimumExecutions: 30,
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/anomaly_detection_rule", 
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

            object AnomalyRuleExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "pipeline_id" -> 1,
                        "metric_field" -> "total_rows",
                        "z_threshold" -> 3.0,
                        "lookback_days" -> 30,
                        "minimum_executions" -> 30
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/anomaly_detection_rule"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

2. **Response**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.0,
        "lookback_days": 30,
        "minimum_executions": 5,
        "active": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": null
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

      .. tab:: Python

         .. code-block:: python

            import httpx

            # Define rules to create
            rules = [
                {
                    "pipeline_id": 1,
                    "metric_field": "total_rows",
                    "z_threshold": 2.0,
                    "lookback_days": 30,
                    "minimum_executions": 5
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "duration_seconds",
                    "z_threshold": 2.5,
                    "lookback_days": 30,
                    "minimum_executions": 10
                },
                {
                    "pipeline_id": 1,
                    "metric_field": "throughput",
                    "z_threshold": 1.8,
                    "lookback_days": 30,
                    "minimum_executions": 8
                }
            ]

            # Create all rules
            for rule in rules:
                response = httpx.post(
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
                   "lookback_days": 30,
                   "minimum_executions": 30
                 }'

            # Monitor execution time anomalies
            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "duration_seconds",
                   "z_threshold": 3.0,
                   "lookback_days": 30,
                   "minimum_executions": 30
                 }'

            # Monitor throughput anomalies
            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "throughput",
                   "z_threshold": 3.0,
                   "lookback_days": 30,
                   "minimum_executions": 30
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

            type AnomalyRule struct {
                PipelineID        int     `json:"pipeline_id"`
                MetricField       string  `json:"metric_field"`
                ZThreshold        float64 `json:"z_threshold"`
                LookbackDays      int     `json:"lookback_days"`
                MinimumExecutions int     `json:"minimum_executions"`
            }

            func main() {
                rules := []AnomalyRule{
                    {1, "total_rows", 2.0, 30, 5},
                    {1, "duration_seconds", 2.5, 30, 10},
                    {1, "throughput", 1.8, 30, 8},
                }
                
                for _, rule := range rules {
                    jsonData, _ := json.Marshal(rule)
                    resp, _ := http.Post("http://localhost:8000/anomaly_detection_rule", 
                        "application/json", bytes.NewBuffer(jsonData))
                    defer resp.Body.Close()
                    
                    var result map[string]interface{}
                    json.NewDecoder(resp.Body).Decode(&result)
                    fmt.Printf("%s rule: %v\n", rule.MetricField, result)
                }
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object MultipleRulesExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val rules = List(
                        (1, "total_rows", 2.0, 30, 5),
                        (1, "duration_seconds", 2.5, 30, 10),
                        (1, "throughput", 1.8, 30, 8)
                    )
                    
                    rules.foreach { case (pipelineId, metricField, zThreshold, lookbackDays, minExec) =>
                        val json = Json.obj(
                            "pipeline_id" -> pipelineId,
                            "metric_field" -> metricField,
                            "z_threshold" -> zThreshold,
                            "lookback_days" -> lookbackDays,
                            "minimum_executions" -> minExec
                        ).toString()
                        
                        val request = HttpRequest.newBuilder()
                            .uri(URI.create("http://localhost:8000/anomaly_detection_rule"))
                            .header("Content-Type", "application/json")
                            .POST(HttpRequest.BodyPublishers.ofString(json))
                            .build()
                        
                        val response = client.send(request, 
                            HttpResponse.BodyHandlers.ofString())
                        println(s"$metricField rule: ${response.body()}")
                    }
                }
            }

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

- **Automatic**: Runs after every successful execution
- **Background**: Processed by Celery workers
- **Real-time**: Results available immediately
- **Persistent**: Anomaly results stored in database

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

- **violation_value**: The actual metric value that triggered the anomaly
- **z_score**: How many standard deviations from the mean
- **historical_mean**: Average value from historical data
- **std_deviation_value**: Standard deviation from historical data
- **z_threshold**: Configured threshold for this rule
- **threshold_min_value**: Minimum expected value
- **threshold_max_value**: Maximum expected value

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

      .. tab:: Python

         .. code-block:: python

            import httpx

            response = httpx.get("http://localhost:8000/anomaly_detection_rule")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X GET "http://localhost:8000/anomaly_detection_rule"

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "encoding/json"
                "fmt"
                "net/http"
            )

            func main() {
                resp, _ := http.Get("http://localhost:8000/anomaly_detection_rule")
                defer resp.Body.Close()
                
                var result []map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI

            object GetRulesExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/anomaly_detection_rule"))
                        .GET()
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "pipeline_id": 1,
          "metric_field": "total_rows",
          "z_threshold": 2.0,
          "lookback_days": 30,
          "minimum_executions": 5,
          "active": true,
          "created_at": "2024-01-01T10:00:00Z",
          "updated_at": null
        }
      ]

Get specific rule details:

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx

            response = httpx.get("http://localhost:8000/anomaly_detection_rule/1")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X GET "http://localhost:8000/anomaly_detection_rule/1"

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "encoding/json"
                "fmt"
                "net/http"
            )

            func main() {
                resp, _ := http.Get("http://localhost:8000/anomaly_detection_rule/1")
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI

            object GetRuleExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/anomaly_detection_rule/1"))
                        .GET()
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

Updating Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update anomaly detection rules:

   **Response:** Returns the complete updated rule (full AnomalyDetectionRule model)

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx

            response = httpx.patch(
                "http://localhost:8000/anomaly_detection_rule",
                json={
                    "id": 1,
                    "z_threshold": 2.5,
                    "lookback_days": 30,
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
                   "lookback_days": 30,
                   "minimum_executions": 10
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

            type RuleUpdate struct {
                ID                int `json:"id"`
                ZThreshold        float64 `json:"z_threshold"`
                LookbackDays      int `json:"lookback_days"`
                MinimumExecutions int `json:"minimum_executions"`
            }

            func main() {
                data := RuleUpdate{
                    ID:                1,
                    ZThreshold:        2.5,
                    LookbackDays:      30,
                    MinimumExecutions: 10,
                }
                
                jsonData, _ := json.Marshal(data)
                req, _ := http.NewRequest("PATCH", "http://localhost:8000/anomaly_detection_rule", 
                    bytes.NewBuffer(jsonData))
                req.Header.Set("Content-Type", "application/json")
                
                client := &http.Client{}
                resp, _ := client.Do(req)
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

            object UpdateRuleExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "id" -> 1,
                        "z_threshold" -> 2.5,
                        "lookback_days" -> 30,
                        "minimum_executions" -> 10
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/anomaly_detection_rule"))
                        .header("Content-Type", "application/json")
                        .method("PATCH", HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

   **Response Example:**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.5,
        "lookback_days": 30,
        "minimum_executions": 10,
        "active": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T11:30:00Z"
      }

Unflagging Anomalies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unflag anomalies that are false positives:

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx

            response = httpx.post(
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

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type UnflagRequest struct {
                PipelineID        int      `json:"pipeline_id"`
                PipelineExecutionID int    `json:"pipeline_execution_id"`
                MetricField       []string `json:"metric_field"`
            }

            func main() {
                data := UnflagRequest{
                    PipelineID:        1,
                    PipelineExecutionID: 123,
                    MetricField:       []string{"total_rows", "duration_seconds"},
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/unflag_anomaly", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                fmt.Println(resp.StatusCode)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object UnflagExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "pipeline_id" -> 1,
                        "pipeline_execution_id" -> 123,
                        "metric_field" -> Json.arr("total_rows", "duration_seconds")
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/unflag_anomaly"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.statusCode())
                }
            }

This removes the anomaly flags and allows the execution to be included in future baseline calculations.

Adjusting Thresholds
~~~~~~~~~~~~~~~~~~~~

The system provides detailed statistical data to help you fine-tune anomaly detection sensitivity. Each anomaly result includes both the **z-score** (actual deviation) and **z-threshold** (sensitivity setting) to guide adjustments.

Understanding the Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Z-Score vs Z-Threshold:**

- **Z-Score**: How many standard deviations the current value is from the historical mean
- **Z-Threshold**: Your sensitivity setting (e.g., 2.0 = flag anything beyond 2 standard deviations)
- **Relationship**: If `z_score > z_threshold` → Anomaly detected

Tuning Process
~~~~~~~~~~~~~~

You are given the pipeline execution id in the alert message. You can utilize this to query the `anomaly_detection_result` table:

.. code-block:: sql

   SELECT
   /* Current Values */
   adr.pipeline_execution_id,
   rule.metric_field,
   adr.violation_value,
   adr.historical_mean,
   adr.std_deviation_value,
   adr.z_threshold,
   adr.threshold_min_value,
   adr.threshold_max_value,

   /* Z-Score for analysis */
   adr.z_score,
   FLOOR(0, adr.historical_mean - (adr.std_deviation_value * adr.z_score)) AS new_threshold_min_value,
   adr.historical_mean + (adr.std_deviation_value * adr.z_score) AS new_threshold_max_value
   FROM public.anomaly_detection_result AS adr
   INNER JOIN public.anomaly_detection_rule AS rule
       ON rule.id = adr.rule_id
   WHERE pipeline_execution_id = 12  /* Grab from Alert */
       AND rule.metric_field = 'DURATION_SECONDS'  /* Grab from Alert */

This gives you information around how close the `violation_value` was to the threshold and what a new threshold would look like if adjusted to the violation value and its z_score. This gives you an idea of how to adjust the `z_threshold` to mitigate false positives.

Best Practices
---------------

Rule Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Start Conservative**: Begin with higher z-thresholds (2.5-3.0)
- **Adjust Based on Data**: Lower thresholds as you understand your data patterns
- **Multiple Metrics**: Monitor different aspects of pipeline performance
- **Sufficient History**: Ensure enough historical data for stable baselines

Threshold Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A good rule of thumb is to start with a z-threshold of 3.0 and a minimum executions of 30. 
According to the Central Limit Theorem, 30 executions is enough to get a stable baseline for normal distrbution.

Monitoring Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Regular Review**: Review anomaly results regularly
- **False Positive Management**: Unflag false positives promptly
- **Threshold Tuning**: Adjust thresholds based on results
- **Alert Fatigue**: Avoid overly sensitive thresholds

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
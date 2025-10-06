Log Cleanup & Maintenance
==========================

The log cleanup system provides automated maintenance for historical data, helping you manage database growth and maintain optimal performance by removing old log records while preserving recent data for analysis and monitoring.

How It Works
~~~~~~~~~~~~

The log cleanup system identifies and removes old records from log tables based on a configurable retention period:

1. **Retention Calculation**: Calculates a cutoff date based on current date minus retention days
2. **Batch Processing**: Deletes records in configurable batches to avoid database locks
3. **Cascading Cleanup**: Removes related records from dependent tables in the correct order
4. **Progress Tracking**: Reports the number of records deleted from each table

Configuration
~~~~~~~~~~~~~

**Input Parameters**

- **retention_days**: Number of days to retain data (minimum: 90 days)
- **batch_size**: Number of records to delete per batch (default: 10,000)

API Usage
~~~~~~~~~

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         cleanup_data = {
             "retention_days": 90,
             "batch_size": 5000
         }

         response = httpx.post(
             "http://localhost:8000/log_cleanup",
             json=cleanup_data
         )
         result = response.json()
         print(result)

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/log_cleanup" \
              -H "Content-Type: application/json" \
              -d '{
                "retention_days": 90,
                "batch_size": 5000
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

         type CleanupRequest struct {
             RetentionDays int `json:"retention_days"`
             BatchSize     int `json:"batch_size"`
         }

         func main() {
             data := CleanupRequest{
                 RetentionDays: 90,
                 BatchSize:     5000,
             }
             
             jsonData, _ := json.Marshal(data)
             resp, _ := http.Post("http://localhost:8000/log_cleanup", 
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

         object LogCleanupExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val json = Json.obj(
                     "retention_days" -> 90,
                     "batch_size" -> 5000
                 ).toString()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/log_cleanup"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(json))
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

**Response Example**

.. code-block:: json

   {
       "total_pipeline_executions_deleted": 150,
       "total_timeliness_pipeline_execution_logs_deleted": 23,
       "total_anomaly_detection_results_deleted": 8,
       "total_pipeline_execution_closure_parent_deleted": 45,
       "total_pipeline_execution_closure_child_deleted": 45,
       "total_freshness_pipeline_logs_deleted": 12
   }

Cleanup Process
~~~~~~~~~~~~~~~

The system cleans up data from six main log tables in a specific order to maintain referential integrity:

**1. Freshness Pipeline Logs**

- **Table**: `freshness_pipeline_log`
- **Filter**: Records with `last_dml_timestamp <= retention_date`
- **Purpose**: Removes old DML freshness check logs

**2. Timeliness Pipeline Execution Logs**

- **Table**: `timeliness_pipeline_execution_log`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old timeliness check logs

**3. Anomaly Detection Results**

- **Table**: `anomaly_detection_result`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old anomaly detection results

**4. Pipeline Execution Closure Table (Parent Side)**

- **Table**: `pipeline_execution_closure`
- **Filter**: Records with `parent_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes closure table relationships where the execution is a parent

**5. Pipeline Execution Closure Table (Child Side)**

- **Table**: `pipeline_execution_closure`
- **Filter**: Records with `child_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes closure table relationships where the execution is a child

**6. Pipeline Executions (Last)**

- **Table**: `pipeline_execution`
- **Filter**: Records with `id <= max_pipeline_execution_id`
- **Purpose**: Removes old pipeline execution records (must be last due to foreign key constraints)

Scheduled Cleanup
~~~~~~~~~~~~~~~~~

**Automated Cleanup with Cron**


Set up automated log cleanup using cron:

.. code-block:: bash

   # Clean up logs daily (365 days retention)
   0 2 * * * curl -X POST http://localhost:8000/log_cleanup -H "Content-Type: application/json" -d '{"retention_days": 365}'

   # Clean up logs weekly (90 days retention)
   0 2 * * 0 curl -X POST http://localhost:8000/log_cleanup -H "Content-Type: application/json" -d '{"retention_days": 90}'


**Programmatic Cleanup**

Use Python scheduling for more control:

.. code-block:: python

   import schedule
   import time
   import requests

   def cleanup_logs():
       cleanup_data = {
           "retention_days": 90,
           "batch_size": 10000
       }
       
       response = requests.post(
           "http://localhost:8000/log_cleanup",
           json=cleanup_data
       )
       
       if response.status_code == 200:
           result = response.json()
           print(f"Cleanup completed: {result}")
       else:
           print(f"Cleanup failed: {response.text}")

   # Schedule cleanup every Sunday at 2 AM
   schedule.every().sunday.at("02:00").do(cleanup_logs)

   # Run the scheduler
   while True:
       schedule.run_pending()
       time.sleep(60)

The log cleanup system helps maintain optimal database performance while preserving the data you need for monitoring and analysis.
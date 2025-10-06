Pipeline Management
====================

This guide covers how to effectively manage data pipelines in Watcher, 
including execution tracking, hierarchical workflows, and organizational best practices.

Creating Pipelines
------------------

Basic Pipeline Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a pipeline (pipeline_type is automatically created if it doesn't exist):

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         pipeline_data = {
             "name": "daily sales pipeline",
             "pipeline_type_name": "extraction",
             "pipeline_metadata": {
                 "description": "Daily extraction of sales data",
                 "owner": "data-team",
                 "schedule": "0 2 * * *"
             }
         }

         response = httpx.post(
             "http://localhost:8000/pipeline",
             json=pipeline_data
         )
         print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/pipeline" \
              -H "Content-Type: application/json" \
              -d '{
                "name": "daily sales pipeline",
                "pipeline_type_name": "extraction",
                "pipeline_metadata": {
                  "description": "Daily extraction of sales data",
                  "owner": "data-team",
                  "schedule": "0 2 * * *"
                }
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

         type PipelineRequest struct {
             Name             string                 `json:"name"`
             PipelineTypeName string                 `json:"pipeline_type_name"`
             PipelineMetadata map[string]interface{} `json:"pipeline_metadata"`
         }

         func main() {
             data := PipelineRequest{
                 Name:             "daily sales pipeline",
                 PipelineTypeName: "extraction",
                 PipelineMetadata: map[string]interface{}{
                     "description": "Daily extraction of sales data",
                     "owner":       "data-team",
                     "schedule":    "0 2 * * *",
                 },
             }
             
             jsonData, _ := json.Marshal(data)
             resp, _ := http.Post("http://localhost:8000/pipeline", 
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

         object PipelineExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val json = Json.obj(
                     "name" -> "daily sales pipeline",
                     "pipeline_type_name" -> "extraction",
                     "pipeline_metadata" -> Json.obj(
                         "description" -> "Daily extraction of sales data",
                         "owner" -> "data-team",
                         "schedule" -> "0 2 * * *"
                     )
                 ).toString()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/pipeline"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(json))
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure monitoring settings during pipeline creation:

.. code-block:: json

   {
     "name": "Customer Data Pipeline",
     "pipeline_type_name": "extraction",
     "next_watermark": "2024-01-01T00:00:00Z",
     "freshness_number": 24,
     "freshness_datepart": "hour",
     "mute_freshness_check": false,
     "timeliness_number": 2,
     "timeliness_datepart": "hour",
     "mute_timeliness_check": false,
     "load_lineage": true
   }

Pipeline Active Flag
~~~~~~~~~~~~~~~~~~~~

The `active` flag allows you to control pipeline execution without deleting the pipeline configuration. This is useful for:

- **Temporary Disabling**: Turn off pipelines during maintenance windows
- **Emergency Response**: Quickly disable failing pipelines to prevent cascading issues

**Default Behavior:**
- New pipelines are `active: true` by default
- The flag is purely informational - your code can check this field to implement custom logic
- Pipeline metadata and configuration are preserved regardless of active status
- The `active` flag is always returned in the /pipeline API response

**Managing Active Status:**

The `active` flag can be updated via the PATCH endpoint:

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         # Disable a pipeline
         update_data = {
             "id": 1,
             "active": False
         }
         
         response = httpx.patch(
             "http://localhost:8000/pipeline",
             json=update_data
         )
         print(response.json())

   .. tab:: curl

      .. code-block:: bash

         # Disable pipeline
         curl -X PATCH "http://localhost:8000/pipeline" \
              -H "Content-Type: application/json" \
              -d '{"id": 1, "active": false}'

   .. tab:: Go

      .. code-block:: go

         package main

         import (
             "bytes"
             "encoding/json"
             "fmt"
             "net/http"
         )

         type PipelineUpdate struct {
             ID     int  `json:"id"`
             Active bool `json:"active"`
         }

         func main() {
             data := PipelineUpdate{
                 ID:     1,
                 Active: true,
             }
             
             jsonData, _ := json.Marshal(data)
             req, _ := http.NewRequest("PATCH", "http://localhost:8000/pipeline", 
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

         object PipelineUpdateExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 val json = Json.obj(
                     "id" -> 1,
                     "active" -> true
                 ).toString()
                 
                 val request = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/pipeline"))
                     .header("Content-Type", "application/json")
                     .method("PATCH", HttpRequest.BodyPublishers.ofString(json))
                     .build()
                 
                 val response = client.send(request, 
                     HttpResponse.BodyHandlers.ofString())
                 println(response.body())
             }
         }

**Practical Example:**

Here's a complete example showing how to create/get a pipeline and use the `active` flag:

.. code-block:: python

   import requests

   def run_pipeline_if_active(pipeline_name: str, pipeline_type: str):
       """Create or get pipeline and run only if active."""
       
       # Create or get pipeline
       pipeline_data = {
           "name": pipeline_name,
           "pipeline_type_name": pipeline_type
       }
       
       response = requests.post(
           "http://localhost:8000/pipeline",
           json=pipeline_data
       )
       pipeline = response.json()
       
       # Check active flag before proceeding
       if not pipeline["active"]:
           print(f"Pipeline '{pipeline_name}' is inactive, skipping execution")
           return
       
       print(f"Pipeline '{pipeline_name}' is active, proceeding with execution")
       
       # Your pipeline logic here
       # - Data extraction
       # - Data transformation  
       # - Data loading
       # - etc.
       
       print("Pipeline execution completed successfully")

   # Usage
   run_pipeline_if_active("daily sales pipeline", "extraction")

Pipeline Execution
------------------

Starting and Ending Executions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         # Start execution
         start_data = {
             "pipeline_id": 1,
             "start_date": "2024-01-01T10:00:00Z",
             "full_load": True
         }

         start_response = httpx.post(
             "http://localhost:8000/start_pipeline_execution",
             json=start_data
         )
         execution_id = start_response.json()["id"]
         print(f"Execution started: {execution_id}")

         # Your pipeline code executes here
         # - Data extraction/transformation logic
         # - Database operations
         # - File processing
         # - API calls
         # - Any other business logic

         # End execution
         end_data = {
             "id": execution_id,
             "pipeline_id": 1,
             "end_date": "2024-01-01T10:05:00Z",
             "completed_successfully": True,
             "total_rows": 10000,
             "inserts": 8000,
             "updates": 2000,
             "soft_deletes": 0
         }

         end_response = httpx.post(
             "http://localhost:8000/end_pipeline_execution",
             json=end_data
         )
         print(end_response.json())

   .. tab:: curl

      .. code-block:: bash

         # Start execution
         curl -X POST "http://localhost:8000/start_pipeline_execution" \
              -H "Content-Type: application/json" \
              -d '{
                "pipeline_id": 1,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": true
              }'

         # Your pipeline code executes here
         # - Data extraction/transformation logic
         # - Database operations
         # - File processing
         # - API calls
         # - Any other business logic

         # End execution
         curl -X POST "http://localhost:8000/end_pipeline_execution" \
              -H "Content-Type: application/json" \
              -d '{
                "id": 1,
                "pipeline_id": 1,
                "end_date": "2024-01-01T10:05:00Z",
                "completed_successfully": true,
                "total_rows": 10000,
                "inserts": 8000,
                "updates": 2000,
                "soft_deletes": 0
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

         type StartExecution struct {
             PipelineID int    `json:"pipeline_id"`
             StartDate  string `json:"start_date"`
             FullLoad   bool   `json:"full_load"`
         }

         type EndExecution struct {
             ID                  int `json:"id"`
             PipelineID          int `json:"pipeline_id"`
             EndDate             string `json:"end_date"`
             CompletedSuccessfully bool `json:"completed_successfully"`
             TotalRows           int `json:"total_rows"`
             Inserts             int `json:"inserts"`
             Updates             int `json:"updates"`
             SoftDeletes         int `json:"soft_deletes"`
         }

         func main() {
             // Start execution
             startData := StartExecution{
                 PipelineID: 1,
                 StartDate:  "2024-01-01T10:00:00Z",
                 FullLoad:   true,
             }
             
             jsonData, _ := json.Marshal(startData)
             resp, _ := http.Post("http://localhost:8000/start_pipeline_execution", 
                 "application/json", bytes.NewBuffer(jsonData))
             defer resp.Body.Close()
             
             var startResult map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&startResult)
             executionID := int(startResult["id"].(float64))
             fmt.Printf("Execution started: %d\n", executionID)

             // Your pipeline code executes here
             // - Data extraction/transformation logic
             // - Database operations
             // - File processing
             // - API calls
             // - Any other business logic

             // End execution
             endData := EndExecution{
                 ID:                  executionID,
                 PipelineID:          1,
                 EndDate:             "2024-01-01T10:05:00Z",
                 CompletedSuccessfully: true,
                 TotalRows:           10000,
                 Inserts:             8000,
                 Updates:             2000,
                 SoftDeletes:         0,
             }
             
             jsonData, _ = json.Marshal(endData)
             resp, _ = http.Post("http://localhost:8000/end_pipeline_execution", 
                 "application/json", bytes.NewBuffer(jsonData))
             defer resp.Body.Close()
             
             var endResult map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&endResult)
             fmt.Println(endResult)
         }

   .. tab:: Scala

      .. code-block:: scala

         import java.net.http.{HttpClient, HttpRequest, HttpResponse}
         import java.net.URI
         import play.api.libs.json.Json

         object PipelineExecutionExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 // Start execution
                 val startJson = Json.obj(
                     "pipeline_id" -> 1,
                     "start_date" -> "2024-01-01T10:00:00Z",
                     "full_load" -> true
                 ).toString()
                 
                 val startRequest = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/start_pipeline_execution"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(startJson))
                     .build()
                 
                 val startResponse = client.send(startRequest, 
                     HttpResponse.BodyHandlers.ofString())
                 val startResult = Json.parse(startResponse.body())
                 val executionId = (startResult \ "id").as[Int]
                 println(s"Execution started: $executionId")

                 // Your pipeline code executes here
                 // - Data extraction/transformation logic
                 // - Database operations
                 // - File processing
                 // - API calls
                 // - Any other business logic

                 // End execution
                 val endJson = Json.obj(
                     "id" -> executionId,
                     "pipeline_id" -> 1,
                     "end_date" -> "2024-01-01T10:05:00Z",
                     "completed_successfully" -> true,
                     "total_rows" -> 10000,
                     "inserts" -> 8000,
                     "updates" -> 2000,
                     "soft_deletes" -> 0
                 ).toString()
                 
                 val endRequest = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/end_pipeline_execution"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(endJson))
                     .build()
                 
                 val endResponse = client.send(endRequest, 
                     HttpResponse.BodyHandlers.ofString())
                 println(endResponse.body())
             }
         }

Execution Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Full Load Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-01T10:00:00Z",
     "full_load": true
   }

**Incremental Load Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-02T10:00:00Z",
     "full_load": false,
     "next_watermark": "2024-01-02T23:59:59Z"
   }

**Nested Execution Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-01T10:00:00Z",
     "full_load": true,
     "parent_id": 5
   }

Pipeline Updates
----------------

Common Update Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Change Monitoring Thresholds**

.. code-block:: json

   {
     "id": 1,
     "freshness_number": 48,
     "freshness_datepart": "hour",
     "timeliness_number": 4,
     "timeliness_datepart": "hour"
   }

**Mute Monitoring Checks**

.. code-block:: json

   {
     "id": 1,
     "mute_freshness_check": true,
     "mute_timeliness_check": true
   }

**Update Watermark**

.. code-block:: json

   {
     "id": 1,
     "next_watermark": "2024-01-02T00:00:00Z"
   }

Nested Pipeline Executions
--------------------------

Watcher supports hierarchical pipeline execution tracking through the `parent_id` field, enabling you to model complex workflows with sub-pipelines and dependencies.

**Use Cases:**

- **Main Pipeline**: A main orchestration pipeline that coordinates multiple sub-pipelines
- **Sub-Pipeline Tracking**: Individual components or steps within a larger workflow
- **Dependency Management**: Track which sub-pipelines depend on others
- **Performance Analysis**: Analyze execution times at both main and sub-pipeline levels
- **Error Isolation**: Identify which specific sub-pipeline failed within a complex workflow

**Example Workflow:**

.. code-block:: text

   Main Pipeline: data_processing_main
   ├── Sub-Pipeline: extract_sales_data (parent_id: main_execution_id)
   ├── Sub-Pipeline: extract_marketing_data (parent_id: main_execution_id)
   ├── Sub-Pipeline: transform_combined_data (parent_id: main_execution_id)
   └── Sub-Pipeline: load_to_warehouse (parent_id: main_execution_id)

**API Usage:**

.. tabs::

   .. tab:: Python

      .. code-block:: python

         import httpx

         # Start main pipeline execution
         main_response = httpx.post(
             "http://localhost:8000/start_pipeline_execution",
             json={
                 "pipeline_id": 1,
                 "start_date": "2024-01-01T10:00:00Z",
                 "full_load": True
             }
         )
         main_execution_id = main_response.json()["id"]

         # Start sub-pipeline with parent reference
         sub_response = httpx.post(
             "http://localhost:8000/start_pipeline_execution",
             json={
                 "pipeline_id": 2,
                 "start_date": "2024-01-01T10:00:00Z",
                 "full_load": True,
                 "parent_id": main_execution_id
             }
         )

   .. tab:: curl

      .. code-block:: bash

         # Start main pipeline execution
         curl -X POST "http://localhost:8000/start_pipeline_execution" \
              -H "Content-Type: application/json" \
              -d '{
                "pipeline_id": 1,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": true
              }'

         # Start sub-pipeline with parent reference
         curl -X POST "http://localhost:8000/start_pipeline_execution" \
              -H "Content-Type: application/json" \
              -d '{
                "pipeline_id": 2,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": true,
                "parent_id": 123
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

         type StartExecution struct {
             PipelineID int    `json:"pipeline_id"`
             StartDate  string `json:"start_date"`
             FullLoad   bool   `json:"full_load"`
             ParentID   *int   `json:"parent_id,omitempty"`
         }

         func main() {
             // Start main pipeline execution
             mainData := StartExecution{
                 PipelineID: 1,
                 StartDate:  "2024-01-01T10:00:00Z",
                 FullLoad:   true,
             }
             
             jsonData, _ := json.Marshal(mainData)
             resp, _ := http.Post("http://localhost:8000/start_pipeline_execution", 
                 "application/json", bytes.NewBuffer(jsonData))
             defer resp.Body.Close()
             
             var mainResult map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&mainResult)
             mainExecutionID := int(mainResult["id"].(float64))

             // Start sub-pipeline with parent reference
             subData := StartExecution{
                 PipelineID: 2,
                 StartDate:  "2024-01-01T10:00:00Z",
                 FullLoad:   true,
                 ParentID:   &mainExecutionID,
             }
             
             jsonData, _ = json.Marshal(subData)
             resp, _ = http.Post("http://localhost:8000/start_pipeline_execution", 
                 "application/json", bytes.NewBuffer(jsonData))
             defer resp.Body.Close()
             
             var subResult map[string]interface{}
             json.NewDecoder(resp.Body).Decode(&subResult)
             fmt.Println("Sub-pipeline started:", subResult)
         }

   .. tab:: Scala

      .. code-block:: scala

         import java.net.http.{HttpClient, HttpRequest, HttpResponse}
         import java.net.URI
         import play.api.libs.json.Json

         object NestedPipelineExample {
             def main(args: Array[String]): Unit = {
                 val client = HttpClient.newHttpClient()
                 
                 // Start main pipeline execution
                 val mainJson = Json.obj(
                     "pipeline_id" -> 1,
                     "start_date" -> "2024-01-01T10:00:00Z",
                     "full_load" -> true
                 ).toString()
                 
                 val mainRequest = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/start_pipeline_execution"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(mainJson))
                     .build()
                 
                 val mainResponse = client.send(mainRequest, 
                     HttpResponse.BodyHandlers.ofString())
                 val mainResult = Json.parse(mainResponse.body())
                 val mainExecutionId = (mainResult \ "id").as[Int]

                 // Start sub-pipeline with parent reference
                 val subJson = Json.obj(
                     "pipeline_id" -> 2,
                     "start_date" -> "2024-01-01T10:00:00Z",
                     "full_load" -> true,
                     "parent_id" -> mainExecutionId
                 ).toString()
                 
                 val subRequest = HttpRequest.newBuilder()
                     .uri(URI.create("http://localhost:8000/start_pipeline_execution"))
                     .header("Content-Type", "application/json")
                     .POST(HttpRequest.BodyPublishers.ofString(subJson))
                     .build()
                 
                 val subResponse = client.send(subRequest, 
                     HttpResponse.BodyHandlers.ofString())
                 println("Sub-pipeline started:", subResponse.body())
             }
         }

Querying Nested Executions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system automatically maintains a closure table (`pipeline_execution_closure`) that enables efficient querying of hierarchical relationships without recursive queries.

**Closure Table Structure:**

- `parent_execution_id`: The ancestor execution ID
- `child_execution_id`: The descendant execution ID  
- `depth`: The relationship depth (0 = self-reference, 1 = direct child, 2 = grandchild, etc.)

**Example Queries:**

.. code-block:: sql

   -- Get all direct children of an execution
   SELECT pe.* 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.child_execution_id
   WHERE pec.parent_execution_id = 123 
       AND pec.depth = 1;

   -- Get all downstream dependencies of an execution
   SELECT pe.* 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.child_execution_id
   WHERE pec.parent_execution_id = 123 
       AND pec.depth > 0;

   -- Get all upstream dependencies of an execution
   SELECT pe.* 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.parent_execution_id
   WHERE pec.child_execution_id = 456 
       AND pec.depth > 0;

**Benefits:**

- **Hierarchical Monitoring**: Track both overall workflow progress and individual component performance
- **Dependency Tracking**: Understand which sub-pipelines are blocking others
- **Root Cause Analysis**: Quickly identify which specific component caused a failure
- **Resource Optimization**: Analyze which sub-pipelines consume the most time/resources
- **Audit Trail**: Complete visibility into complex multi-step data processes

Pipeline Organization
-----------------------

Effective organization of your Watcher metadata is crucial for maintainability, monitoring, and team collaboration.

**Best Practices:**

1. **Consistency**: Use the same naming patterns across all teams and projects
2. **Descriptiveness**: Names should clearly indicate purpose and scope
3. **Hierarchy**: Use underscores to create logical hierarchies
4. **Future-Proofing**: Choose names that will remain relevant as systems evolve
5. **Documentation**: Document your naming conventions and share with all teams
6. **Validation**: Implement naming validation in your CI/CD pipeline or code reviews

Pipeline Type Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Organize pipeline types by data processing patterns or business domains or a combination of both:

**Data Processing Pattern:**

- `extraction` - Data extraction pipelines
- `transformation` - Data transformation and processing
- `loading` - Data loading and materialization
- `audit` - Data quality and validation
- `monitoring` - System monitoring and health checks  

**Business Domain:**

- `sales`
- `marketing`
- `finance` 

**Combination:**

- `sales_extraction`
- `marketing_audit`
- `finance_monitoring`

Pipeline Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a clear naming structure that matches back to the pipeline code (e.g., DAG name, job name, or workflow identifier).

**Best Practices:**

- Match your DAG/job/workflow names exactly
- Use consistent abbreviations across your organization
- Keep names descriptive but concise
- Use underscores for separation, avoid special characters
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

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         pipeline_data = {
             "name": "daily sales pipeline",
             "pipeline_type_name": "extraction",
             "pipeline_metadata": {
                 "description": "Daily extraction of sales data",
                 "owner": "data-team",
                 "schedule": "0 2 * * *"
             }
         }

         response = requests.post(
             "http://localhost:8000/pipeline",
             json=pipeline_data
         )
         print(response.json())

   .. tab:: Python - httpx

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

         with httpx.Client() as client:
             response = client.post(
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

   .. tab:: HTTPie

      .. code-block:: bash

         http POST localhost:8000/pipeline \
              name="daily sales pipeline" \
              pipeline_type_name=extraction \
              pipeline_metadata:='{"description": "Daily extraction of sales data", "owner": "data-team", "schedule": "0 2 * * *"}'

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

Pipeline Execution
------------------

Starting and Ending Executions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         # Start execution
         start_data = {
             "pipeline_id": 1,
             "start_date": "2024-01-01T10:00:00Z",
             "full_load": True
         }

         start_response = requests.post(
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

         end_response = requests.post(
             "http://localhost:8000/end_pipeline_execution",
             json=end_data
         )
         print(end_response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             # Start execution
             start_data = {
                 "pipeline_id": 1,
                 "start_date": "2024-01-01T10:00:00Z",
                 "full_load": True
             }

             start_response = client.post(
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

             end_response = client.post(
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

   .. tab:: HTTPie

      .. code-block:: bash

         # Start execution
         http POST localhost:8000/start_pipeline_execution \
              pipeline_id=1 \
              start_date="2024-01-01T10:00:00Z" \
              full_load=true

         # Your pipeline code executes here
         # - Data extraction/transformation logic
         # - Database operations
         # - File processing
         # - API calls
         # - Any other business logic

         # End execution
         http POST localhost:8000/end_pipeline_execution \
              id=1 \
              pipeline_id=1 \
              end_date="2024-01-01T10:05:00Z" \
              completed_successfully=true \
              total_rows=10000 \
              inserts=8000 \
              updates=2000 \
              soft_deletes=0

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

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         # Start main pipeline execution
         main_response = requests.post(
             "http://localhost:8000/start_pipeline_execution",
             json={
                 "pipeline_id": 1,
                 "start_date": "2024-01-01T10:00:00Z",
                 "full_load": True
             }
         )
         main_execution_id = main_response.json()["id"]

         # Start sub-pipeline with parent reference
         sub_response = requests.post(
             "http://localhost:8000/start_pipeline_execution",
             json={
                 "pipeline_id": 2,
                 "start_date": "2024-01-01T10:00:00Z",
                 "full_load": True,
                 "parent_id": main_execution_id
             }
         )

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             # Start main pipeline execution
             main_response = client.post(
                 "http://localhost:8000/start_pipeline_execution",
                 json={
                     "pipeline_id": 1,
                     "start_date": "2024-01-01T10:00:00Z",
                     "full_load": True
                 }
             )
             main_execution_id = main_response.json()["id"]

             # Start sub-pipeline with parent reference
             sub_response = client.post(
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

   .. tab:: HTTPie

      .. code-block:: bash

         # Start main pipeline execution
         http POST localhost:8000/start_pipeline_execution \
              pipeline_id=1 \
              start_date="2024-01-01T10:00:00Z" \
              full_load=true

         # Start sub-pipeline with parent reference
         http POST localhost:8000/start_pipeline_execution \
              pipeline_id=2 \
              start_date="2024-01-01T10:00:00Z" \
              full_load=true \
              parent_id=123

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
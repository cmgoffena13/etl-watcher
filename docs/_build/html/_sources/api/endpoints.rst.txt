API Endpoints
=============

This section documents all available API endpoints in Watcher.

Pipeline Management
-------------------

Create or Get Pipeline
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /pipeline

   Create a new pipeline or get existing one.

   **Request Body:**

   .. code-block:: json

      {
        "name": "My Data Pipeline",
        "pipeline_type_name": "extraction",
        "next_watermark": "2024-01-02T00:00:00Z",
        "pipeline_metadata": {
          "description": "Daily data extraction pipeline"
        }
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "active": true,
        "load_lineage": true,
        "watermark": "2024-01-01T00:00:00Z"
      }

List Pipelines
~~~~~~~~~~~~~~

.. http:get:: /pipeline

   Get all pipelines.

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "name": "my data pipeline",
          "pipeline_type_id": 1,
          "watermark": "2024-01-01T00:00:00Z",
          "next_watermark": "2024-01-01T23:59:59Z",
          "active": true,
          "load_lineage": true,
          "created_at": "2024-01-01T10:00:00Z",
          "updated_at": "2024-01-01T10:00:00Z"
        }
      ]

Get Pipeline by ID
~~~~~~~~~~~~~~~~~~

.. http:get:: /pipeline/{pipeline_id}

   Get a specific pipeline by ID.

   **Parameters:**
   
   - ``pipeline_id`` (int): Pipeline ID

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "my data pipeline",
        "pipeline_type_id": 1,
        "watermark": "2024-01-01T00:00:00Z",
        "next_watermark": "2024-01-01T23:59:59Z",
        "active": true,
        "load_lineage": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      }

Update Pipeline
~~~~~~~~~~~~~~~

.. http:patch:: /pipeline

   Update pipeline configuration.

   **Request Body:**

   .. code-block:: json

      {
        "id": 1,
        "name": "Updated Pipeline Name",
        "next_watermark": "2024-01-02T00:00:00Z"
      }

Pipeline Execution
------------------

Start Pipeline Execution
~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /start_pipeline_execution

   Start a new pipeline execution.

   **Request Body:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "start_date": "2024-01-01T10:00:00Z",
        "full_load": true,
        "watermark": "2024-01-01T00:00:00Z",
        "next_watermark": "2024-01-01T23:59:59Z",
        "parent_id": null,
        "execution_metadata": {
          "trigger": "scheduled"
        }
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

End Pipeline Execution
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /end_pipeline_execution

   End a pipeline execution with metrics.

   **Request Body:**

   .. code-block:: json

      {
        "id": 1,
        "end_date": "2024-01-01T10:05:00Z",
        "completed_successfully": true,
        "total_rows": 1000,
        "inserts": 800,
        "updates": 200,
        "soft_deletes": 0
      }

Pipeline Types
--------------

Create or Get Pipeline Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /pipeline_type

   Create a new pipeline type or get existing one.

   **Request Body:**

   .. code-block:: json

      {
        "name": "extraction",
        "group_name": "databricks"
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

List Pipeline Types
~~~~~~~~~~~~~~~~~~~

.. http:get:: /pipeline_type

   Get all pipeline types.

Get Pipeline Type by ID
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /pipeline_type/{pipeline_type_id}

   Get a specific pipeline type by ID.

Address Management
------------------

Create or Get Address
~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address

   Create a new address or get existing one.

   **Request Body:**

   .. code-block:: json

      {
        "name": "my_table",
        "address_type_name": "databricks",
        "address_type_group_name": "database"
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "active": true,
        "load_lineage": true,
        "watermark": null
      }

List Addresses
~~~~~~~~~~~~~~

.. http:get:: /address

   Get all addresses.

Get Address by ID
~~~~~~~~~~~~~~~~

.. http:get:: /address/{address_id}

   Get a specific address by ID.

Update Address
~~~~~~~~~~~~~~

.. http:patch:: /address

   Update address information.

Address Types
-------------

Create or Get Address Type
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address_type

   Create a new address type or get existing one.

   **Request Body:**

   .. code-block:: json

      {
        "name": "databricks",
        "group_name": "database"
      }

List Address Types
~~~~~~~~~~~~~~~~~~

.. http:get:: /address_type

   Get all address types.

Get Address Type by ID
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /address_type/{address_type_id}

   Get a specific address type by ID.

Data Lineage
------------

Create Address Lineage
~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address_lineage

   Create lineage relationships between addresses.

   **Request Body:**

   .. code-block:: json

      {
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
      }

   **Response:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "lineage_relationships_created": 1,
        "message": "Lineage relationships created successfully"
      }

Get Address Lineage
~~~~~~~~~~~~~~~~~~~

.. http:get:: /address_lineage/{address_id}

   Get lineage for specific address.

   **Response:**

   .. code-block:: json

      [
        {
          "source_address_id": 1,
          "target_address_id": 2,
          "depth": 1,
          "source_address_name": "source_table",
          "target_address_name": "target_table"
        }
      ]

Anomaly Detection
-----------------

Create Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /anomaly_detection_rule

   Create or get anomaly detection rule.

   **Request Body:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.0,
        "minimum_executions": 5
      }

   **Response:**

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

List Anomaly Detection Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /anomaly_detection_rule

   Get all anomaly detection rules.

Get Anomaly Detection Rule by ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /anomaly_detection_rule/{anomaly_detection_rule_id}

   Get a specific anomaly detection rule by ID.

Update Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:patch:: /anomaly_detection_rule

   Update anomaly detection rule.

Unflag Anomalies
~~~~~~~~~~~~~~~~

.. http:post:: /unflag_anomaly

   Unflag anomalies for a pipeline execution.

   **Request Body:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "pipeline_execution_id": 1,
        "metric_field": ["total_rows", "duration_seconds"]
      }

Monitoring & Health
-------------------

Check Timeliness
~~~~~~~~~~~~~~~~

.. http:post:: /timeliness

   Check pipeline execution timeliness.

   **Request Body:**

   .. code-block:: json

      {
        "lookback_minutes": 60
      }

   **Response:**

   .. code-block:: json

      {
        "status": "queued"
      }

Check Freshness
~~~~~~~~~~~~~~

.. http:post:: /freshness

   Check DML operation freshness.

   **Response:**

   .. code-block:: json

      {
        "status": "queued"
      }

Log Cleanup
~~~~~~~~~~~

.. http:post:: /log_cleanup

   Clean up old log data.

   **Response:**

   .. code-block:: json

      {
        "total_pipeline_executions_deleted": 1000,
        "total_timeliness_pipeline_execution_logs_deleted": 500,
        "total_anomaly_detection_results_deleted": 50,
        "total_pipeline_execution_closure_parent_deleted": 200,
        "total_pipeline_execution_closure_child_deleted": 200,
        "total_freshness_pipeline_logs_deleted": 300
      }

Celery Queue Monitoring
~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /celery/monitor-queue

   Trigger Celery queue monitoring and alerting.

   **Response:**

   .. code-block:: json

      {
        "status": "success",
        "message": "Queue monitoring completed",
        "queues_checked": 1,
        "total_messages": 0
      }

Diagnostics
-----------

System Diagnostics
~~~~~~~~~~~~~~~~~~

.. http:get:: /diagnostics

   Get comprehensive system diagnostics.

   **Response:** HTML page with system health information

Reporting
---------

Daily Pipeline Metrics
~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /reporting

   Get daily pipeline metrics with pagination and filtering.

   **Query Parameters:**

   - ``page`` (int): Page number (default: 1)
   - ``page_size`` (int): Items per page (default: 50)
   - ``pipeline_id`` (int): Filter by pipeline ID
   - ``start_date`` (str): Start date filter
   - ``end_date`` (str): End date filter

Interactive Documentation
------------------------

Scalar API Documentation
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /scalar

   Interactive API documentation using Scalar for an intuitive interface to explore and test all available endpoints.

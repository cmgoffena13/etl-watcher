API Endpoints
=============

This section documents all available API endpoints in Watcher.

Pipeline Management
-------------------

Create or Get Pipeline
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /pipeline

   Create a new pipeline or get existing one (upsert behavior). Automatically creates pipeline type if it doesn't exist.

   **Request Body:**

   .. code-block:: json

      {
        "name": "my data pipeline",
        "pipeline_type_name": "extraction",
        "watermark": "2024-01-01T00:00:00Z",
        "next_watermark": "2024-01-02T00:00:00Z",
        "pipeline_metadata": {
          "description": "Daily data extraction pipeline"
        },
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false,
        "load_lineage": true
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "active": true,
        "load_lineage": true,
        "watermark": "2024-01-01T00:00:00Z"
      }

   **Request Body Fields:**

   - ``name`` (string): Pipeline name (1-150 characters, required)
   - ``pipeline_type_name`` (string): Pipeline type name (1-150 characters, required)
   - ``watermark`` (string|int|datetime|date): Watermark value (optional)
   - ``next_watermark`` (string|int|datetime|date): Next watermark value (optional)
   - ``pipeline_metadata`` (object): Additional pipeline metadata (optional)
   - ``freshness_number`` (int): Freshness check interval number (optional, >0)
   - ``freshness_datepart`` (string): Freshness check date part (optional, hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted (optional, default: false)
   - ``timeliness_number`` (int): Timeliness check interval number (optional, >0)
   - ``timeliness_datepart`` (string): Timeliness check date part (optional, hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted (optional, default: false)
   - ``load_lineage`` (bool): Whether to load lineage (optional)

   **Response Fields:**

   - ``id`` (int): Pipeline ID
   - ``active`` (bool): Whether pipeline is active
   - ``load_lineage`` (bool): Whether to load lineage
   - ``watermark`` (string|int|datetime|date): Current watermark value (returned when next_watermark is provided)

   **Status Codes:**

   - ``201`` Created - New pipeline was created
   - ``200`` OK - Existing pipeline was found
   - ``500`` Internal Server Error - Unique constraint violation

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
          "pipeline_metadata": {
            "environment": "production"
          },
          "last_target_insert": "2024-01-01T10:00:00Z",
          "last_target_update": "2024-01-01T10:00:00Z",
          "last_target_soft_delete": null,
          "freshness_number": 24,
          "freshness_datepart": "hour",
          "mute_freshness_check": false,
          "timeliness_number": 2,
          "timeliness_datepart": "hour",
          "mute_timeliness_check": false,
          "load_lineage": true,
          "active": true,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T12:00:00Z"
        },
        {
          "id": 2,
          "name": "another pipeline",
          "pipeline_type_id": 2,
          "watermark": null,
          "next_watermark": null,
          "pipeline_metadata": null,
          "last_target_insert": null,
          "last_target_update": null,
          "last_target_soft_delete": null,
          "freshness_number": 48,
          "freshness_datepart": "hour",
          "mute_freshness_check": true,
          "timeliness_number": 4,
          "timeliness_datepart": "hour",
          "mute_timeliness_check": false,
          "load_lineage": false,
          "active": true,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": null
        }
      ]

   **Response Fields:**

   - ``id`` (int): Pipeline ID
   - ``name`` (string): Pipeline name (1-150 characters)
   - ``pipeline_type_id`` (int): Pipeline type ID
   - ``watermark`` (string): Watermark value (max 50 characters, nullable)
   - ``next_watermark`` (string): Next watermark value (max 50 characters, nullable)
   - ``pipeline_metadata`` (object): Pipeline metadata (JSONB, nullable)
   - ``last_target_insert`` (string): Last target insert timestamp (ISO 8601, nullable)
   - ``last_target_update`` (string): Last target update timestamp (ISO 8601, nullable)
   - ``last_target_soft_delete`` (string): Last target soft delete timestamp (ISO 8601, nullable)
   - ``freshness_number`` (int): Freshness check interval number (nullable)
   - ``freshness_datepart`` (string): Freshness check date part (hour, day, week, month, year, nullable)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted
   - ``timeliness_number`` (int): Timeliness check interval number (nullable)
   - ``timeliness_datepart`` (string): Timeliness check date part (hour, day, week, month, year, nullable)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted
   - ``load_lineage`` (bool): Whether to load lineage
   - ``active`` (bool): Whether pipeline is active
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Pipelines retrieved successfully

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
        "pipeline_metadata": {
          "environment": "production"
        },
        "last_target_insert": "2024-01-01T10:00:00Z",
        "last_target_update": "2024-01-01T10:00:00Z",
        "last_target_soft_delete": null,
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false,
        "load_lineage": true,
        "active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }

   **Response Fields:**

   - ``id`` (int): Pipeline ID
   - ``name`` (string): Pipeline name (1-150 characters)
   - ``pipeline_type_id`` (int): Pipeline type ID
   - ``watermark`` (string): Watermark value (max 50 characters)
   - ``next_watermark`` (string): Next watermark value (max 50 characters)
   - ``pipeline_metadata`` (object): Pipeline metadata (JSONB)
   - ``last_target_insert`` (string): Last target insert timestamp (ISO 8601, nullable)
   - ``last_target_update`` (string): Last target update timestamp (ISO 8601, nullable)
   - ``last_target_soft_delete`` (string): Last target soft delete timestamp (ISO 8601, nullable)
   - ``freshness_number`` (int): Freshness check interval number
   - ``freshness_datepart`` (string): Freshness check date part (hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted
   - ``timeliness_number`` (int): Timeliness check interval number
   - ``timeliness_datepart`` (string): Timeliness check date part (hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted
   - ``load_lineage`` (bool): Whether to load lineage
   - ``active`` (bool): Whether pipeline is active
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Pipeline found
   - ``404`` Not Found - Pipeline not found

Update Pipeline
~~~~~~~~~~~~~~~

.. http:patch:: /pipeline

   Update pipeline configuration.

   **Request Body:**

   .. code-block:: json

      {
        "id": 1,
        "name": "updated pipeline name",
        "pipeline_type_id": 2,
        "watermark": "2024-01-01T00:00:00Z",
        "next_watermark": "2024-01-02T00:00:00Z",
        "pipeline_metadata": {
          "environment": "production"
        },
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false,
        "load_lineage": true
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "updated pipeline name",
        "pipeline_type_id": 2,
        "watermark": "2024-01-01T00:00:00Z",
        "next_watermark": "2024-01-02T00:00:00Z",
        "pipeline_metadata": {
          "environment": "production"
        },
        "last_target_insert": "2024-01-01T10:00:00Z",
        "last_target_update": "2024-01-01T10:00:00Z",
        "last_target_soft_delete": null,
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false,
        "load_lineage": true,
        "active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }

   **Request Body Fields:**

   - ``id`` (int): Pipeline ID (required)
   - ``name`` (string): Pipeline name (1-150 characters, optional)
   - ``pipeline_type_id`` (int): Pipeline type ID (optional)
   - ``watermark`` (string|int|datetime|date): Watermark value (optional)
   - ``next_watermark`` (string|int|datetime|date): Next watermark value (optional)
   - ``pipeline_metadata`` (object): Additional pipeline metadata (optional)
   - ``freshness_number`` (int): Freshness check interval number (optional, >0)
   - ``freshness_datepart`` (string): Freshness check date part (optional, hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted (optional)
   - ``timeliness_number`` (int): Timeliness check interval number (optional, >0)
   - ``timeliness_datepart`` (string): Timeliness check date part (optional, hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted (optional)
   - ``load_lineage`` (bool): Whether to load lineage (optional)

   **Response Fields:**

   - ``id`` (int): Pipeline ID
   - ``name`` (string): Pipeline name
   - ``pipeline_type_id`` (int): Pipeline type ID
   - ``watermark`` (string): Watermark value
   - ``next_watermark`` (string): Next watermark value
   - ``pipeline_metadata`` (object): Pipeline metadata
   - ``last_target_insert`` (string): Last target insert timestamp (ISO 8601, nullable)
   - ``last_target_update`` (string): Last target update timestamp (ISO 8601, nullable)
   - ``last_target_soft_delete`` (string): Last target soft delete timestamp (ISO 8601, nullable)
   - ``freshness_number`` (int): Freshness check interval number
   - ``freshness_datepart`` (string): Freshness check date part
   - ``mute_freshness_check`` (bool): Whether freshness check is muted
   - ``timeliness_number`` (int): Timeliness check interval number
   - ``timeliness_datepart`` (string): Timeliness check date part
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted
   - ``load_lineage`` (bool): Whether to load lineage
   - ``active`` (bool): Whether pipeline is active
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601)

   **Status Codes:**

   - ``200`` OK - Pipeline updated successfully
   - ``404`` Not Found - Pipeline not found

Pipeline Execution
------------------

Start Pipeline Execution
~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /start_pipeline_execution

   Start a new pipeline execution. Automatically calculates hour_recorded and date_recorded.

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

   **Request Body Fields:**

   - ``pipeline_id`` (int): Pipeline ID (required)
   - ``start_date`` (string): Start timestamp (ISO 8601, required)
   - ``full_load`` (bool): Whether this is a full load (required)
   - ``watermark`` (string|int|datetime|date): Watermark value (optional)
   - ``next_watermark`` (string|int|datetime|date): Next watermark value (optional)
   - ``parent_id`` (int): Parent execution ID for hierarchical executions (optional)
   - ``execution_metadata`` (object): Additional execution metadata (optional)

   **Response Fields:**

   - ``id`` (int): Pipeline execution ID

   **Status Codes:**

   - ``201`` Created - Pipeline execution started successfully

End Pipeline Execution
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /end_pipeline_execution

   End a pipeline execution with metrics. Automatically calculates duration and throughput.

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

   **Response:**
   HTTP 204 No Content

   **Request Body Fields:**

   - ``id`` (int): Pipeline execution ID (required)
   - ``end_date`` (string): End timestamp (ISO 8601, required)
   - ``completed_successfully`` (bool): Whether execution completed successfully (optional)
   - ``total_rows`` (int): Total rows processed (optional, ≥0)
   - ``inserts`` (int): Number of inserts (optional, ≥0)
   - ``updates`` (int): Number of updates (optional, ≥0)
   - ``soft_deletes`` (int): Number of soft deletes (optional, ≥0)

   **Status Codes:**

   - ``204`` No Content - Pipeline execution ended successfully
   - ``400`` Bad Request - end_date must be greater than start_date
   - ``404`` Not Found - Pipeline execution not found
   - ``500`` Internal Server Error - Database integrity error

Pipeline Types
--------------

Create or Get Pipeline Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /pipeline_type

   Create a new pipeline type or get existing one (upsert behavior).

   **Request Body:**

   .. code-block:: json

      {
        "name": "extraction",
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

   **Request Body Fields:**

   - ``name`` (string): Pipeline type name (1-150 characters, required)
   - ``freshness_number`` (int): Freshness check interval number (optional, >0)
   - ``freshness_datepart`` (string): Freshness check date part (optional, hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted (optional, default: false)
   - ``timeliness_number`` (int): Timeliness check interval number (optional, >0)
   - ``timeliness_datepart`` (string): Timeliness check date part (optional, hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted (optional, default: false)

   **Response Fields:**
   - ``id`` (int): Pipeline type ID

   **Status Codes:**

   - ``201`` Created - New pipeline type was created
   - ``200`` OK - Existing pipeline type was found
   - ``500`` Internal Server Error - Unique constraint violation

List Pipeline Types
~~~~~~~~~~~~~~~~~~~

.. http:get:: /pipeline_type

   Get all pipeline types.

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "name": "extraction",
          "freshness_number": 24,
          "freshness_datepart": "hour",
          "mute_freshness_check": false,
          "timeliness_number": 2,
          "timeliness_datepart": "hour",
          "mute_timeliness_check": false,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T12:00:00Z"
        },
        {
          "id": 2,
          "name": "transformation",
          "freshness_number": 48,
          "freshness_datepart": "hour",
          "mute_freshness_check": true,
          "timeliness_number": 4,
          "timeliness_datepart": "hour",
          "mute_timeliness_check": false,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": null
        }
      ]

   **Response Fields:**

   - ``id`` (int): Pipeline type ID
   - ``name`` (string): Pipeline type name (1-150 characters)
   - ``freshness_number`` (int): Freshness check interval number
   - ``freshness_datepart`` (string): Freshness check date part (hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted
   - ``timeliness_number`` (int): Timeliness check interval number
   - ``timeliness_datepart`` (string): Timeliness check date part (hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Pipeline types retrieved successfully

Get Pipeline Type by ID
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /pipeline_type/{pipeline_type_id}

   Get a specific pipeline type by ID.

   **Parameters:**
   - ``pipeline_type_id`` (int): Pipeline type ID

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "extraction",
        "freshness_number": 24,
        "freshness_datepart": "hour",
        "mute_freshness_check": false,
        "timeliness_number": 2,
        "timeliness_datepart": "hour",
        "mute_timeliness_check": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }

   **Response Fields:**

   - ``id`` (int): Pipeline type ID
   - ``name`` (string): Pipeline type name (1-150 characters)
   - ``freshness_number`` (int): Freshness check interval number
   - ``freshness_datepart`` (string): Freshness check date part (hour, day, week, month, year)
   - ``mute_freshness_check`` (bool): Whether freshness check is muted
   - ``timeliness_number`` (int): Timeliness check interval number
   - ``timeliness_datepart`` (string): Timeliness check date part (hour, day, week, month, year)
   - ``mute_timeliness_check`` (bool): Whether timeliness check is muted
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Pipeline type found
   - ``404`` Not Found - Pipeline type not found

Address Management
------------------

Create or Get Address
~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address

   Create a new address or get existing one (upsert behavior). Automatically creates address type if it doesn't exist.

   **Request Body:**

   .. code-block:: json

      {
        "name": "source_db.source_schema.source_table",
        "address_type_name": "postgres",
        "address_type_group_name": "database",
        "database_name": "source_db",
        "schema_name": "source_schema",
        "table_name": "source_table",
        "primary_key": "id",
        "deprecated": false
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

   **Request Body Fields:**

   - ``name`` (string): Address name (1-150 characters, required)
   - ``address_type_name`` (string): Address type name (1-150 characters, required)
   - ``address_type_group_name`` (string): Address type group name (1-150 characters, required)
   - ``database_name`` (string): Database name (max 50 characters, optional)
   - ``schema_name`` (string): Schema name (max 50 characters, optional)
   - ``table_name`` (string): Table name (max 50 characters, optional)
   - ``primary_key`` (string): Primary key (max 50 characters, optional)
   - ``deprecated`` (bool): Whether address is deprecated (optional, default: false)

   **Response Fields:**

   - ``id`` (int): Address ID

   **Status Codes:**

   - ``201`` Created - New address was created
   - ``200`` OK - Existing address was found

List Addresses
~~~~~~~~~~~~~~

.. http:get:: /address

   Get all addresses.

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "name": "source_db.source_schema.source_table",
          "address_type_id": 1,
          "database_name": "source_db",
          "schema_name": "source_schema",
          "table_name": "source_table",
          "primary_key": "id",
          "deprecated": false,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T12:00:00Z"
        },
        {
          "id": 2,
          "name": "target_db.target_schema.target_table",
          "address_type_id": 1,
          "database_name": "target_db",
          "schema_name": "target_schema",
          "table_name": "target_table",
          "primary_key": "id",
          "deprecated": false,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": null
        }
      ]

   **Response Fields:**

   - ``id`` (int): Address ID
   - ``name`` (string): Address name (1-150 characters)
   - ``address_type_id`` (int): Address type ID
   - ``database_name`` (string): Database name (max 50 characters)
   - ``schema_name`` (string): Schema name (max 50 characters)
   - ``table_name`` (string): Table name (max 50 characters)
   - ``primary_key`` (string): Primary key (max 50 characters)
   - ``deprecated`` (bool): Whether address is deprecated
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Addresses retrieved successfully

Get Address by ID
~~~~~~~~~~~~~~~~

.. http:get:: /address/{address_id}

   Get a specific address by ID.

   **Parameters:**
   - ``address_id`` (int): Address ID

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "source_db.source_schema.source_table",
        "address_type_id": 1,
        "database_name": "source_db",
        "schema_name": "source_schema",
        "table_name": "source_table",
        "primary_key": "id",
        "deprecated": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }

   **Response Fields:**

   - ``id`` (int): Address ID
   - ``name`` (string): Address name (1-150 characters)
   - ``address_type_id`` (int): Address type ID
   - ``database_name`` (string): Database name (max 50 characters)
   - ``schema_name`` (string): Schema name (max 50 characters)
   - ``table_name`` (string): Table name (max 50 characters)
   - ``primary_key`` (string): Primary key (max 50 characters)
   - ``deprecated`` (bool): Whether address is deprecated
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Address found
   - ``404`` Not Found - Address not found

Update Address
~~~~~~~~~~~~~~

.. http:patch:: /address

   Update address information.

   **Request Body:**

   .. code-block:: json

      {
        "id": 1,
        "name": "updated_table_name",
        "database_name": "updated_db",
        "schema_name": "updated_schema",
        "table_name": "updated_table",
        "primary_key": "id",
        "deprecated": false,
        "address_type_id": 2
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "updated_table_name",
        "address_type_id": 2,
        "database_name": "updated_db",
        "schema_name": "updated_schema",
        "table_name": "updated_table",
        "primary_key": "id",
        "deprecated": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }

   **Request Body Fields:**

   - ``id`` (int): Address ID (required)
   - ``name`` (string): Address name (1-150 characters, optional)
   - ``address_type_id`` (int): Address type ID (optional)
   - ``database_name`` (string): Database name (max 50 characters, optional)
   - ``schema_name`` (string): Schema name (max 50 characters, optional)
   - ``table_name`` (string): Table name (max 50 characters, optional)
   - ``primary_key`` (string): Primary key (max 50 characters, optional)
   - ``deprecated`` (bool): Whether address is deprecated (optional)

   **Response Fields:**

   - ``id`` (int): Address ID
   - ``name`` (string): Address name
   - ``address_type_id`` (int): Address type ID
   - ``database_name`` (string): Database name
   - ``schema_name`` (string): Schema name
   - ``table_name`` (string): Table name
   - ``primary_key`` (string): Primary key
   - ``deprecated`` (bool): Whether address is deprecated
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601)

   **Status Codes:**

   - ``200`` OK - Address updated successfully
   - ``404`` Not Found - Address not found

Address Types
-------------

Create or Get Address Type
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address_type

   Create a new address type or get existing one (upsert behavior).

   **Request Body:**

   .. code-block:: json

      {
        "name": "postgres",
        "group_name": "database"
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

   **Request Body Fields:**

   - ``name`` (string): Address type name (1-150 characters, required)
   - ``group_name`` (string): Address type group name (1-150 characters, required)

   **Response Fields:**

   - ``id`` (int): Address type ID

   **Status Codes:**

   - ``201`` Created - New address type was created
   - ``200`` OK - Existing address type was found

List Address Types
~~~~~~~~~~~~~~~~~~

.. http:get:: /address_type

   Get all address types.

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "name": "postgres",
          "group_name": "database",
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T00:00:00Z"
        },
        {
          "id": 2,
          "name": "mysql",
          "group_name": "database",
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": null
        }
      ]

   **Response Fields:**

   - ``id`` (int): Address type ID
   - ``name`` (string): Address type name (1-150 characters)
   - ``group_name`` (string): Address type group name (1-150 characters)
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Address types retrieved successfully

Get Address Type by ID
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /address_type/{address_type_id}

   Get a specific address type by ID.

   **Parameters:**
   - ``address_type_id`` (int): Address type ID

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "name": "postgres",
        "group_name": "database",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }

   **Response Fields:**

   - ``id`` (int): Address type ID
   - ``name`` (string): Address type name (1-150 characters)
   - ``group_name`` (string): Address type group name (1-150 characters)
   - ``created_at`` (string): Creation timestamp (ISO 8601)
   - ``updated_at`` (string): Last update timestamp (ISO 8601, nullable)

   **Status Codes:**

   - ``200`` OK - Address type found
   - ``404`` Not Found - Address type not found

Address Lineage
------------

Create Address Lineage
~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /address_lineage

   Create lineage relationships between addresses. Automatically creates addresses and address types if they don't exist.

   **Request Body:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "source_addresses": [
          {
            "name": "source_db.source_schema.source_table",
            "address_type_name": "postgres",
            "address_type_group_name": "database"
          }
        ],
        "target_addresses": [
          {
            "name": "target_db.target_schema.target_table",
            "address_type_name": "postgres",
            "address_type_group_name": "database"
          }
        ]
      }

   **Response:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "lineage_relationships_created": 1,
        "message": "Lineage relationships created for pipeline 1"
      }

   **Request Body Fields:**

   - ``pipeline_id`` (int): Pipeline ID (required)
   - ``source_addresses`` (array): List of source addresses
   - ``target_addresses`` (array): List of target addresses
   - ``name`` (string): Address name (1-150 characters)
   - ``address_type_name`` (string): Address type name (1-150 characters)
   - ``address_type_group_name`` (string): Address type group name (1-150 characters)

   **Response Fields:**

   - ``pipeline_id`` (int): Pipeline ID
   - ``lineage_relationships_created`` (int): Number of relationships created
   - ``message`` (string): Status message

   **Status Codes:**

   - ``201`` Created - Lineage relationships created successfully
   - ``200`` OK - Pipeline does not have load_lineage=True, no relationships created

Get Address Lineage
~~~~~~~~~~~~~~~~~~~

.. http:get:: /address_lineage/{address_id}

   Get lineage relationships for a specific address using the closure table.
   Returns all relationships where the address is either source or target.

   **Parameters:**

   - ``address_id`` (int): Address ID to get lineage for

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

   **Response Fields:**

   - ``source_address_id`` (int): Source address ID
   - ``target_address_id`` (int): Target address ID  
   - ``depth`` (int): Relationship depth (0 = direct, >0 = transitive)
   - ``source_address_name`` (string): Source address name
   - ``target_address_name`` (string): Target address name

Anomaly Detection
-----------------

Create or Get Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /anomaly_detection_rule

   Create a new anomaly detection rule or get existing one (upsert behavior).

   **Request Body:**

   .. code-block:: json

      {
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.0,
        "lookback_days": 30,
        "minimum_executions": 30,
        "active": true
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1
      }

   **Parameters:**

   - ``pipeline_id`` (int): Pipeline ID (required)
   - ``metric_field`` (string): Metric field to monitor (required)
   - ``z_threshold`` (float): Z-score threshold 1.0-10.0 (default: 3.0)
   - ``lookback_days`` (int): Days of historical data 1-365 (default: 30)
   - ``minimum_executions`` (int): Minimum executions 5-1000 (default: 30)
   - ``active`` (bool): Whether rule is active (default: true)

   **Status Codes:**

   - ``201`` Created - New rule was created
   - ``200`` OK - Existing rule was found

List Anomaly Detection Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /anomaly_detection_rule

   Get all anomaly detection rules.

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "pipeline_id": 1,
          "metric_field": "total_rows",
          "z_threshold": 2.0,
          "lookback_days": 30,
          "minimum_executions": 30,
          "active": true,
          "created_at": "2024-01-01T10:00:00Z",
          "updated_at": "2024-01-01T10:05:00Z"
        },
        {
          "id": 2,
          "pipeline_id": 1,
          "metric_field": "duration_seconds",
          "z_threshold": 3.0,
          "lookback_days": 30,
          "minimum_executions": 30,
          "active": true,
          "created_at": "2024-01-01T10:00:00Z",
          "updated_at": null
        }
      ]

Get Anomaly Detection Rule by ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /anomaly_detection_rule/{anomaly_detection_rule_id}

   Get a specific anomaly detection rule by ID.

   **Parameters:**

   - ``anomaly_detection_rule_id`` (int): Rule ID

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "total_rows",
        "z_threshold": 2.0,
        "lookback_days": 30,
        "minimum_executions": 30,
        "active": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:05:00Z"
      }

Update Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:patch:: /anomaly_detection_rule

   Update anomaly detection rule.

   **Request Body:**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "updates",
        "z_threshold": 2.5,
        "lookback_days": 30,
        "minimum_executions": 20,
        "active": true
      }

   **Response:**

   .. code-block:: json

      {
        "id": 1,
        "pipeline_id": 1,
        "metric_field": "updates",
        "z_threshold": 2.5,
        "lookback_days": 30,
        "minimum_executions": 20,
        "active": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:05:00Z"
      }

   **Parameters:**

   - ``id`` (int): Rule ID (required)
   - ``pipeline_id`` (int): Pipeline ID (optional)
   - ``metric_field`` (string): Metric field to monitor (optional)
   - ``z_threshold`` (float): Z-score threshold 1.0-10.0 (optional)
   - ``lookback_days`` (int): Days of historical data 1-365 (optional)
   - ``minimum_executions`` (int): Minimum executions 5-1000 (optional)
   - ``active`` (bool): Whether rule is active (optional)

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

   **Response:** HTTP 204 No Content

   **Parameters:**

   - ``pipeline_id`` (int): Pipeline ID
   - ``pipeline_execution_id`` (int): Pipeline execution ID
   - ``metric_field`` (array): List of metric fields to unflag

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

   Clean up old log data based on retention period.

   **Request Body:**

   .. code-block:: json

      {
        "retention_days": 90,
        "batch_size": 10000
      }

   **Parameters:**

   - ``retention_days`` (int): Number of days to retain data (minimum: 90)
   - ``batch_size`` (int): Number of records to delete per batch (default: 10000)

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

   Monitor Celery queue depths and alert if queue gets too big.

   **Request Body:** None

   **Response:**

   .. code-block:: json

      {
        "status": "success"
      }

   **Error Response:**

   .. code-block:: json

      {
        "status": "error"
      }

   **Alert Thresholds:**

   - **WARNING**: 50+ pending tasks
   - **CRITICAL**: 100+ pending tasks

Diagnostics Web Page
-------------------

System Diagnostics
~~~~~~~~~~~~~~~~~~

.. http:get:: /diagnostics

   Web-based diagnostics dashboard providing comprehensive system health monitoring 
   and performance analysis.

   **Features:**

   - Database health and connection performance testing
   - Schema health checks and index usage statistics
   - Celery worker status and task performance monitoring
   - Deadlock statistics and active query analysis
   - Long-running query identification
   - Real-time system metrics

   **Response:**

   HTML dashboard interface

   **Sections:**
   
   - **Connection Speed Test** - Raw asyncpg connection performance testing and direct database connectivity validation
   - **Connection Performance** - Comprehensive connection scenarios (raw asyncpg, SQLAlchemy engine, pool behavior, DNS resolution) and connection pool analysis
   - **Schema Health Check** - Table sizes, row counts, index usage statistics, missing indexes identification, unused indexes detection, and table statistics
   - **Performance & Locks** - Deadlock statistics and trends, currently locked tables, top active queries with duration and wait events, and long-running queries (>30s) identification
   - **Celery Health** - Worker status, task performance, queue monitoring, and background task diagnostics

   **Access:**
   - **URL**: http://localhost:8000/diagnostics
   - **Method**: GET
   - **Content-Type**: text/html

Reporting Dashboard Web Page
----------------------------

Pipeline Performance Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /reporting

   Web-based reporting dashboard providing daily pipeline performance metrics and analytics.

   **Features:**
   
   - Daily aggregations of pipeline execution data
   - Performance metrics (throughput, duration, error rates)
   - Pipeline type and name filtering
   - Time range filtering (last 1-30 days)
   - Real-time data from materialized views
   - Auto-refresh capabilities

   **Response:**

   HTML dashboard interface

   **Data Source:**

   Built on the ``daily_pipeline_report`` materialized view for fast query performance.

   **Access:**

   - **URL**: http://localhost:8000/reporting
   - **Method**: GET
   - **Content-Type**: text/html

Interactive API Documentation
------------------------

Scalar API Documentation
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /scalar

   Interactive API documentation using Scalar for an intuitive interface to explore and test all available endpoints.

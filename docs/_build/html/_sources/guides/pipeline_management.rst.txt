Pipeline Management
====================

This guide covers how to effectively manage data pipelines in Watcher.

Creating Pipelines
------------------

Basic Pipeline Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create a pipeline type first**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/pipeline_type" \
           -H "Content-Type: application/json" \
           -d '{
             "name": "extraction",
             "group_name": "databricks"
           }'

2. **Create the pipeline**

   .. code-block:: bash

      curl -X POST "http://localhost:8000/pipeline" \
           -H "Content-Type: application/json" \
           -d '{
             "name": "Daily Sales Pipeline",
             "pipeline_type_name": "extraction",
             "next_watermark": "2024-01-01T00:00:00Z",
             "pipeline_metadata": {
               "description": "Daily extraction of sales data",
               "owner": "data-team",
               "schedule": "0 2 * * *"
             }
           }'

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

Starting Executions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start a pipeline execution**

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
             "total_rows": 10000,
             "inserts": 8000,
             "updates": 2000,
             "soft_deletes": 0
           }'

Execution Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Full Load Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-01T10:00:00Z",
     "full_load": true,
     "watermark": "2024-01-01T00:00:00Z",
     "next_watermark": "2024-01-01T23:59:59Z"
   }

**Incremental Load Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-02T10:00:00Z",
     "full_load": false,
     "watermark": "2024-01-01T23:59:59Z",
     "next_watermark": "2024-01-02T23:59:59Z"
   }

**Nested Execution Pattern**

.. code-block:: json

   {
     "pipeline_id": 1,
     "start_date": "2024-01-01T10:00:00Z",
     "full_load": true,
     "watermark": "2024-01-01T00:00:00Z",
     "next_watermark": "2024-01-01T23:59:59Z",
     "parent_id": null,
     "execution_metadata": {
       "trigger": "scheduled",
       "batch_id": "batch_001"
     }
   }

Watermark Management
-------------------

Understanding Watermarks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watermarks track the progress of data processing:

- **watermark** Current position (where processing has reached)
- **next_watermark** Target position (where processing should go to)

Watermark Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Daily Processing**

.. code-block:: json

   {
     "watermark": "2024-01-01T00:00:00Z",
     "next_watermark": "2024-01-01T23:59:59Z"
   }

**Hourly Processing**

.. code-block:: json

   {
     "watermark": "2024-01-01T10:00:00Z",
     "next_watermark": "2024-01-01T11:00:00Z"
   }

**Numeric Watermarks**

.. code-block:: json

   {
     "watermark": "1000",
     "next_watermark": "2000"
   }

Watermark Increment Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After successful execution, the watermark is automatically updated:

1. **Execution completes successfully**
2. **Pipeline watermark becomes next_watermark**
3. **Next execution starts from the new watermark**

Example Flow:

.. code-block:: text

   Execution 1: watermark=0, next_watermark=1000 → Success → watermark=1000
   Execution 2: watermark=1000, next_watermark=2000 → Success → watermark=2000
   Execution 3: watermark=2000, next_watermark=3000 → Success → watermark=3000

Pipeline Monitoring
-------------------

Freshness Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor data freshness to ensure data is up-to-date:

.. code-block:: bash

   curl -X POST "http://localhost:8000/freshness"
   
   # Response
   {
     "status": "queued"
   }

Timeliness Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor pipeline execution timing:

.. code-block:: bash

   curl -X POST "http://localhost:8000/timeliness" \
        -H "Content-Type: application/json" \
        -d '{
          "lookback_minutes": 60
        }'
   
   # Response
   {
     "status": "queued"
   }

Monitoring Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure monitoring thresholds in pipeline creation:

.. code-block:: json

   {
     "name": "Critical Data Pipeline",
     "pipeline_type_name": "extraction",
     "freshness_number": 1,
     "freshness_datepart": "hour",
     "mute_freshness_check": false,
     "timeliness_number": 30,
     "timeliness_datepart": "minute",
     "mute_timeliness_check": false
   }

Anomaly Detection
------------------

Setting Up Anomaly Detection
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

2. **Anomaly detection runs automatically** after each successful execution

Supported Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor various pipeline metrics:

- **total_rows** Total number of rows processed
- **duration_seconds** Execution duration
- **throughput** Rows processed per second
- **inserts** Number of insert operations
- **updates** Number of update operations
- **soft_deletes** Number of soft delete operations

Z-Score Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure sensitivity of anomaly detection:

- **1.5** Very sensitive (catches minor variations)
- **2.0** Standard sensitivity (recommended)
- **2.5** Less sensitive (catches major variations)
- **3.0** Very conservative (catches only extreme anomalies)

Data Lineage
------------

Creating Lineage Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track relationships between data sources:

.. code-block:: bash

      curl -X POST "http://localhost:8000/address_lineage" \
           -H "Content-Type: application/json" \
           -d '{
             "pipeline_id": 1,
             "source_addresses": [
               {
                 "name": "raw_sales_data",
                 "address_type_name": "databricks",
                 "address_type_group_name": "database"
               }
             ],
             "target_addresses": [
               {
                 "name": "processed_sales_data",
                 "address_type_name": "databricks",
                 "address_type_group_name": "database"
               }
             ]
           }'

Querying Lineage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get lineage information for an address:

.. code-block:: bash

   curl -X GET "http://localhost:8000/address_lineage/1"
   
   # Response
   [
     {
       "source_address_id": 1,
       "target_address_id": 2,
       "depth": 1,
       "source_address_name": "raw_sales_data",
       "target_address_name": "processed_sales_data"
     }
   ]

Pipeline Updates
----------------

Updating Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update pipeline settings:

.. code-block:: bash

   curl -X PATCH "http://localhost:8000/pipeline" \
        -H "Content-Type: application/json" \
        -d '{
          "id": 1,
          "name": "Updated Pipeline Name",
          "next_watermark": "2024-01-02T00:00:00Z",
          "mute_freshness_check": true
        }'

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

Best Practices
--------------

Pipeline Design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Clear Naming** Use descriptive names for pipelines
- **Consistent Watermarks** Use consistent watermark formats
- **Metadata** Include relevant metadata for context
- **Monitoring** Configure appropriate monitoring thresholds

Execution Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Regular Executions** Run pipelines on consistent schedules
- **Proper Metrics** Always provide accurate execution metrics
- **Error Handling** Handle failures gracefully
- **Documentation** Document pipeline behavior and dependencies

Monitoring Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Appropriate Thresholds** Set realistic monitoring thresholds
- **Regular Checks** Run monitoring checks regularly
- **Alert Configuration** Configure appropriate alerting
- **Performance Tracking** Monitor execution performance trends

Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Watermark Not Updating**
- Check if execution completed successfully
- Verify next_watermark is provided
- Check for database connection issues

**Monitoring Alerts**
- Review monitoring thresholds
- Check data freshness and timeliness
- Verify pipeline execution schedules

**Anomaly Detection**
- Ensure sufficient historical data
- Check z-score thresholds
- Verify metric field selection

**Lineage Issues**
- Verify address creation
- Check lineage relationship creation
- Review closure table maintenance

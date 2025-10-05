Celery Tasks
============

This section documents all Celery background tasks in Watcher.

Task Overview
-------------

Watcher uses Celery for distributed background task processing, providing reliable execution of monitoring checks, anomaly detection, and data processing tasks.

Task Types
----------

detect_anomalies_task
~~~~~~~~~~~~~~~~~~~~

**Purpose** Statistical analysis of pipeline execution patterns

**Rate Limit** 15/s

**Parameters**
- ``pipeline_id`` (int): Pipeline ID to analyze
- ``pipeline_execution_id`` (int): Execution ID to analyze

**Description** 
Automatically triggered after each successful pipeline execution. Performs statistical analysis on pipeline metrics to detect anomalies using z-score analysis.

**Retry Policy**
- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Example**

.. code-block:: python

   from src.celery_tasks import detect_anomalies_task
   
   # Trigger anomaly detection
   detect_anomalies_task.delay(pipeline_id=1, pipeline_execution_id=123)

freshness_check_task
************************************~

**Purpose** DML operation monitoring and data staleness detection

**Rate Limit** 1/s

**Parameters** None

**Description** 
Monitors data modification operations (inserts, updates, soft deletes) to detect stale data. Checks when data was last modified and alerts if it's older than expected.

**Retry Policy**
- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Example**

.. code-block:: python

   from src.celery_tasks import freshness_check_task
   
   # Trigger freshness check
   freshness_check_task.delay()

timeliness_check_task
****************************************~

**Purpose** Pipeline execution timing validation

**Rate Limit** 1/s

**Parameters**
- ``lookback_minutes`` (int): How far back to look for executions (default: 60)

**Description** 
Validates that pipeline executions are completing within expected timeframes. Compares actual execution times against configured timeliness thresholds.

**Retry Policy**
- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Example**

.. code-block:: python

   from src.celery_tasks import timeliness_check_task
   
   # Trigger timeliness check
   timeliness_check_task.delay(lookback_minutes=120)

address_lineage_closure_rebuild_task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose** Rebuild address lineage closure table relationships

**Rate Limit** 1/s

**Parameters**
- ``connected_addresses`` (List[int]): List of address IDs to rebuild
- ``pipeline_id`` (int): Pipeline ID for context

**Description** 
Maintains the closure table for address lineage relationships. Rebuilds the transitive closure when new lineage relationships are created.

**Retry Policy**
- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Example**

.. code-block:: python

   from src.celery_tasks import address_lineage_closure_rebuild_task
   
   # Rebuild closure table
   address_lineage_closure_rebuild_task.delay(
       connected_addresses=[1, 2, 3],
       pipeline_id=1
   )

pipeline_execution_closure_maintain_task
****************************************************************************~

**Purpose** Maintain pipeline execution hierarchy closure table

**Rate Limit** 10/s

**Parameters**
- ``execution_id`` (int): Execution ID to maintain
- ``parent_id`` (int, optional): Parent execution ID

**Description** 
Maintains the closure table for pipeline execution hierarchies. Automatically triggered when new pipeline executions are created to track parent-child relationships.

**Retry Policy**
- Max retries: 3
- Retry delay: 30 seconds
- Exponential backoff

**Example**

.. code-block:: python

   from src.celery_tasks import pipeline_execution_closure_maintain_task
   
   # Maintain execution hierarchy
   pipeline_execution_closure_maintain_task.delay(
       execution_id=123,
       parent_id=122
   )

Task Configuration
------------------

Rate Limiting
************************~

All tasks have configurable rate limits to prevent system overload:

- **detect_anomalies_task** 15/s (high frequency for real-time analysis)
- **freshness_check_task** 1/s (low frequency for periodic checks)
- **timeliness_check_task** 1/s (low frequency for periodic checks)
- **address_lineage_closure_rebuild_task** 1/s (low frequency for maintenance)
- **pipeline_execution_closure_maintain_task** 10/s (medium frequency for hierarchy maintenance)

Retry Policies
~~~~~~~~~~~~~~

All tasks implement retry policies with exponential backoff:

- **Max Retries** 3 attempts
- **Base Delay** 30-60 seconds depending on task type
- **Exponential Backoff** Delay increases with each retry
- **Final Failure** Task marked as failed after max retries

Error Handling
~~~~~~~~~~~~~~

Tasks include comprehensive error handling:

- **Database Errors** Connection issues, constraint violations
- **Validation Errors** Invalid input parameters
- **Timeout Errors** Long-running operations
- **System Errors** Memory, disk, or network issues

Task Monitoring
----------------

Task Status Tracking
~~~~~~~~~~~~~~~~~~~~

Each task provides status updates during execution:

- **PENDING** Task queued, waiting for worker
- **PROGRESS** Task running, with progress updates
- **SUCCESS** Task completed successfully
- **FAILURE** Task failed with error details
- **RETRY** Task failed, will retry

Progress Updates
~~~~~~~~~~~~~~~~

Tasks provide detailed progress information:

.. code-block:: json

   {
     "state": "PROGRESS",
     "meta": {
       "status": "Processing anomaly detection...",
       "current_step": "Calculating z-scores",
       "progress": 75
     }
   }

Error Details
************************~

Failed tasks include detailed error information:

.. code-block:: json

   {
     "state": "FAILURE",
     "meta": {
       "exc_type": "DatabaseError",
       "exc_message": "Connection timeout",
       "retry_count": 2,
       "max_retries": 3
     }
   }

Queue Management
----------------

Default Queue
************************~

All tasks are processed through the main ``celery`` queue:

- **Queue Name** ``celery``
- **Worker Scaling** Multiple workers can handle the same queue
- **Load Distribution** Tasks distributed across available workers
- **Priority** First-in, first-out (FIFO) processing

Worker Scaling
~~~~~~~~~~~~~~

Workers can be scaled horizontally:

.. code-block:: bash

   # Start multiple workers
   celery -A src.celery_app worker --loglevel=info --concurrency=4
   celery -A src.celery_app worker --loglevel=info --concurrency=4
   celery -A src.celery_app worker --loglevel=info --concurrency=4

Queue Monitoring
~~~~~~~~~~~~~~~~

Monitor queue health and performance:

- **Queue Depth** Number of pending tasks
- **Worker Status** Active workers and their status
- **Task Throughput** Tasks processed per minute
- **Error Rates** Failed task percentages

Alert Thresholds
~~~~~~~~~~~~~~~~

Configure alerts for queue issues:

- **INFO** (20+ messages): Queue building up
- **WARNING** (50+ messages): Queue getting backed up
- **CRITICAL** (100+ messages): Queue severely backed up

Example Alert
~~~~~~~~~~~~

.. code-block:: text

   🚨 CRITICAL
   Celery Queue Alert
   Timestamp: 2025-09-28 06:04:26 UTC
   Message: Queue has 2367 pending tasks
   
   Details:
   • Messages in queue: 2367
   • Scheduled tasks: 0
   • Workers active: 2
   • Queue: celery

Performance Optimization
-----------------------

Task Optimization
~~~~~~~~~~~~~~~~

Optimize task performance:

- **Batch Processing** Process multiple items in single task
- **Async Operations** Use async/await for I/O operations
- **Connection Pooling** Reuse database connections
- **Caching** Cache frequently accessed data

Worker Optimization
************************************~

Optimize worker performance:

- **Concurrency** Adjust worker concurrency based on CPU cores
- **Memory** Monitor memory usage and adjust accordingly
- **Resource Limits** Set appropriate resource limits
- **Health Checks** Implement worker health monitoring

Monitoring Integration
~~~~~~~~~~~~~~~~~~~~~~

Integrate with monitoring systems:

- **Logfire** Automatic task tracking and performance metrics
- **Prometheus** Custom metrics for task performance
- **Grafana** Dashboards for task monitoring
- **Slack** Real-time alerts for task failures

Best Practices
--------------

Task Design
********************~

Design tasks for reliability:

- **Idempotent** Tasks should be safe to retry
- **Atomic** Tasks should complete or fail completely
- **Stateless** Tasks should not depend on external state
- **Timeout** Set appropriate timeouts for long-running tasks

Error Handling
************************~

Implement robust error handling:

- **Validation** Validate all input parameters
- **Graceful Degradation** Handle partial failures gracefully
- **Logging** Log all errors with context
- **Alerting** Alert on critical failures

Monitoring
~~~~~~~~~~

Monitor task health:

- **Success Rates** Track task success percentages
- **Execution Times** Monitor task duration trends
- **Queue Depth** Monitor queue backlog
- **Worker Health** Monitor worker status and performance

Scaling
************~

Scale tasks appropriately:

- **Horizontal Scaling** Add more workers as needed
- **Vertical Scaling** Increase worker resources
- **Load Balancing** Distribute tasks across workers
- **Auto-scaling** Implement automatic scaling based on queue depth

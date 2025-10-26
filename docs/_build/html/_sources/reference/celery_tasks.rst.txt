Celery Tasks
============

This section documents all Celery background tasks in Watcher. Watcher uses Celery for distributed background task processing, providing reliable execution of monitoring checks, anomaly detection, and data processing tasks.

Task Types
----------

Regular Tasks
~~~~~~~~~~~~~

These tasks are triggered by API calls or other events and run in the main ``celery`` queue.

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
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~

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

**Rate Limit** 5/s

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose** Maintain pipeline execution hierarchy closure table

**Rate Limit** - No rate limit (Needs to keep up with pipeline execution creation rate)

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

Scheduled Tasks
~~~~~~~~~~~~~~~

These tasks are automatically scheduled by Celery Beat and run in the ``scheduled`` queue. They provide automated monitoring and maintenance without manual intervention.

scheduled_freshness_check
~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose** Automated freshness monitoring for all active pipelines

**Queue** scheduled

**Schedule** Configurable via ``WATCHER_FRESHNESS_CHECK_SCHEDULE`` (default: ``0 * * * *`` - hourly)

**Parameters** None

**Description** 
Automatically triggers freshness checks for all active pipelines on a configurable schedule. Delegates to the regular ``freshness_check_task``.

**Retry Policy**

- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Configuration**

Set the schedule using environment variable:

.. code-block:: bash

   WATCHER_FRESHNESS_CHECK_SCHEDULE="0 * * * *"  # Every hour

scheduled_timeliness_check
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose** Automated timeliness monitoring for all active pipelines

**Queue** scheduled

**Schedule** Configurable via ``WATCHER_TIMELINESS_CHECK_SCHEDULE`` (default: ``*/15 * * * *`` - every 15 minutes)

**Parameters** None (uses ``WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES`` for lookback)

**Description** 
Automatically triggers timeliness checks for all active pipelines on a configurable schedule. Delegates to the regular ``timeliness_check_task`` with configured lookback period.

**Retry Policy**

- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Configuration**

Set the schedule and lookback period:

.. code-block:: bash

   WATCHER_TIMELINESS_CHECK_SCHEDULE="*/15 * * * *"  # Every 15 minutes
   WATCHER_TIMELINESS_CHECK_LOOKBACK_MINUTES=60      # Look back 60 minutes

scheduled_celery_queue_health_check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose** Automated Celery queue health monitoring and alerting

**Queue** scheduled

**Schedule** Configurable via ``WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE`` (default: ``*/5 * * * *`` - every 5 minutes)

**Parameters** None

**Description** 
Automatically monitors Celery queue health, including task counts, queue depths, and scheduled tasks. Sends Slack alerts when thresholds are exceeded. Delegates to the ``check_celery_queue`` function.

**Retry Policy**

- Max retries: 3
- Retry delay: 60 seconds
- Exponential backoff

**Configuration**

Set the schedule:

.. code-block:: bash

   WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE="*/5 * * * *"  # Every 5 minutes

Task Configuration
------------------

Queue Management
~~~~~~~~~~~~~~~~

Watcher uses two separate Celery queues for task isolation:

- **celery** - Main queue for regular tasks triggered by API calls
- **scheduled** - Dedicated queue for automated scheduled tasks

This separation prevents scheduled monitoring tasks from being delayed by high-volume regular tasks.

Rate Limiting
~~~~~~~~~~~~~

Regular tasks have configurable rate limits to prevent system overload:

- **detect_anomalies_task** 15/s (high frequency for real-time analysis)
- **freshness_check_task** 1/s (low frequency for periodic checks)
- **timeliness_check_task** 1/s (low frequency for periodic checks)
- **address_lineage_closure_rebuild_task** 5/s (medium frequency for maintenance)
- **pipeline_execution_closure_maintain_task** No rate limit (must keep up with execution rate)

Scheduled tasks have no rate limits as they are controlled by Celery Beat scheduling.

Celery Beat Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Celery Beat is configured with the following default schedules:

.. code-block:: python

   celery.conf.beat_schedule = {
       "scheduled-freshness-check": {
           "task": "src.celery_tasks.scheduled_freshness_check",
           "schedule": crontab(minute=0),  # Every hour
       },
       "scheduled-timeliness-check": {
           "task": "src.celery_tasks.scheduled_timeliness_check", 
           "schedule": crontab(minute="*/15"),  # Every 15 minutes
       },
       "scheduled-celery-queue-health-check": {
           "task": "src.celery_tasks.scheduled_celery_queue_health_check",
           "schedule": crontab(minute="*/5"),  # Every 5 minutes
       },
   }

Schedules are configurable via environment variables:

- ``WATCHER_FRESHNESS_CHECK_SCHEDULE``
- ``WATCHER_TIMELINESS_CHECK_SCHEDULE`` 
- ``WATCHER_CELERY_QUEUE_HEALTH_CHECK_SCHEDULE``

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
       "status": "Starting anomaly detection..."
     }
   }

Error Details
~~~~~~~~~~~~~

Failed tasks include comprehensive error information:

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
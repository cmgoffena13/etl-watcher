Pydantic Data Models
============

This section documents the pydantic data models used in Watcher's API for validation request/response bodies

Pipeline Models
---------------

PipelinePostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelinePostInput(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       pipeline_type_name: str = Field(max_length=150, min_length=1)
       next_watermark: Optional[Union[str, int, DateTime, Date]] = None
       pipeline_metadata: Optional[dict] = None
       freshness_number: Optional[int] = Field(default=None, gt=0)
       freshness_datepart: Optional[DatePartEnum] = None
       timeliness_number: Optional[int] = Field(default=None, gt=0)
       timeliness_datepart: Optional[DatePartEnum] = None

PipelinePostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelinePostOutput(ValidatorModel):
       id: int
       active: bool
       load_lineage: bool
       watermark: Optional[Union[str, int, DateTime, Date]] = None

PipelinePatchInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelinePatchInput(ValidatorModel):
       id: int
       name: Optional[str] = Field(None, max_length=150, min_length=1)
       pipeline_type_id: Optional[int] = None
       watermark: Optional[Union[str, int, DateTime, Date]] = None
       next_watermark: Optional[Union[str, int, DateTime, Date]] = None
       pipeline_metadata: Optional[dict] = None
       freshness_number: Optional[int] = Field(None, gt=0)
       freshness_datepart: Optional[DatePartEnum] = None
       mute_freshness_check: Optional[bool] = None
       timeliness_number: Optional[int] = Field(None, gt=0)
       timeliness_datepart: Optional[DatePartEnum] = None
       mute_timeliness_check: Optional[bool] = None
       load_lineage: Optional[bool] = None
       active: Optional[bool] = None

Pipeline Type Models
--------------------

PipelineTypePostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineTypePostInput(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       freshness_number: Optional[int] = Field(None, gt=0)
       freshness_datepart: Optional[DatePartEnum] = None
       mute_freshness_check: Optional[bool] = Field(default=False)
       timeliness_number: Optional[int] = Field(None, gt=0)
       timeliness_datepart: Optional[DatePartEnum] = None
       mute_timeliness_check: Optional[bool] = Field(default=False)

PipelineTypePostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineTypePostOutput(ValidatorModel):
       id: int

PipelineTypePatchInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineTypePatchInput(ValidatorModel):
       id: int
       name: Optional[str] = Field(None, max_length=150, min_length=1)
       freshness_number: Optional[int] = Field(None, gt=0)
       freshness_datepart: Optional[DatePartEnum] = None
       mute_freshness_check: Optional[bool] = None
       timeliness_number: Optional[int] = Field(None, gt=0)
       timeliness_datepart: Optional[DatePartEnum] = None
       mute_timeliness_check: Optional[bool] = None

Pipeline Execution Models
-------------------------

PipelineExecutionStartInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineExecutionStartInput(ValidatorModel):
       pipeline_id: int
       start_date: DateTime
       watermark: Optional[Union[str, int, DateTime, Date]] = None
       next_watermark: Optional[Union[str, int, DateTime, Date]] = None
       parent_id: Optional[int] = None
       execution_metadata: Optional[dict] = None

PipelineExecutionStartOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineExecutionStartOutput(ValidatorModel):
       id: int

PipelineExecutionEndInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class PipelineExecutionEndInput(ValidatorModel):
       id: int
       end_date: DateTime
       completed_successfully: bool
       total_rows: Optional[int] = Field(default=None, ge=0)
       inserts: Optional[int] = Field(default=None, ge=0)
       updates: Optional[int] = Field(default=None, ge=0)
       soft_deletes: Optional[int] = Field(default=None, ge=0)

Address Models
--------------

AddressPostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressPostInput(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       address_type_name: str = Field(max_length=150, min_length=1)
       address_type_group_name: str = Field(max_length=150, min_length=1)
       database_name: Optional[str] = Field(None, max_length=50)
       schema_name: Optional[str] = Field(None, max_length=50)
       table_name: Optional[str] = Field(None, max_length=50)
       primary_key: Optional[str] = Field(None, max_length=50)
       deprecated: Optional[bool] = Field(default=False)

AddressPostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressPostOutput(ValidatorModel):
       id: int

AddressPatchInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressPatchInput(ValidatorModel):
       id: int
       name: Optional[str] = Field(None, max_length=150, min_length=1)
       address_type_id: Optional[int] = None
       database_name: Optional[str] = Field(None, max_length=50)
       schema_name: Optional[str] = Field(None, max_length=50)
       table_name: Optional[str] = Field(None, max_length=50)
       primary_key: Optional[str] = Field(None, max_length=50)
       deprecated: Optional[bool] = Field(default=False)

Address Type Models
-------------------

AddressTypePostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressTypePostInput(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       group_name: str = Field(max_length=150, min_length=1)

AddressTypePostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressTypePostOutput(ValidatorModel):
       id: int

AddressTypePatchInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressTypePatchInput(ValidatorModel):
       id: int
       name: Optional[str] = Field(None, max_length=150, min_length=1)
       group_name: Optional[str] = Field(None, max_length=150, min_length=1)

Address Lineage Models
----------------------

AddressLineagePostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressLineagePostInput(ValidatorModel):
       pipeline_id: int
       source_addresses: List[SourceAddress]
       target_addresses: List[TargetAddress]

SourceAddress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class SourceAddress(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       address_type_name: str = Field(max_length=150, min_length=1)
       address_type_group_name: str = Field(max_length=150, min_length=1)

TargetAddress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class TargetAddress(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       address_type_name: str = Field(max_length=150, min_length=1)
       address_type_group_name: str = Field(max_length=150, min_length=1)

AddressLineagePostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressLineagePostOutput(ValidatorModel):
       pipeline_id: int
       lineage_relationships_created: int
       message: Optional[str] = None

AddressLineageGetOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressLineageGetOutput(ValidatorModel):
       id: int
       pipeline_id: int
       source_address_id: int
       target_address_id: int

AddressLineageClosureGetOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AddressLineageClosureGetOutput(ValidatorModel):
       source_address_id: int
       target_address_id: int
       depth: int
       source_address_name: str
       target_address_name: str

Anomaly Detection Models
------------------------

AnomalyDetectionRulePostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AnomalyDetectionRulePostInput(ValidatorModel):
       pipeline_id: int
       metric_field: AnomalyMetricFieldEnum
       z_threshold: float = Field(gt=0)
       minimum_executions: int = Field(ge=2)

AnomalyDetectionRulePostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AnomalyDetectionRulePostOutput(ValidatorModel):
       id: int
       pipeline_id: int
       metric_field: AnomalyMetricFieldEnum
       z_threshold: float
       minimum_executions: int
       active: bool
       created_at: DateTime

AnomalyDetectionRulePatchInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AnomalyDetectionRulePatchInput(ValidatorModel):
       id: int
       pipeline_id: Optional[int] = None
       metric_field: Optional[AnomalyMetricFieldEnum] = None
       z_threshold: Optional[float] = Field(
           None,
           ge=1.0,
           le=10.0,
           description="How many standard deviations above mean to trigger anomaly",
       )
       lookback_days: Optional[int] = Field(
           None,
           ge=1,
           le=365,
           description="Number of days of historical data to compare against",
       )
       minimum_executions: Optional[int] = Field(
           None,
           ge=5,
           le=1000,
           description="Minimum executions needed for baseline calculation",
       )
       active: Optional[bool] = Field(default=True)

UnflagAnomalyInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class UnflagAnomalyInput(ValidatorModel):
       pipeline_id: int
       pipeline_execution_id: int
       metric_field: List[AnomalyMetricFieldEnum]

Monitoring Models
-----------------

FreshnessPostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class FreshnessPostOutput(ValidatorModel):
       status: str

TimelinessPostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class TimelinessPostInput(ValidatorModel):
       lookback_minutes: int = Field(ge=5, default=60)

TimelinessPostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class TimelinessPostOutput(ValidatorModel):
       status: str

Log Cleanup Models
-----------------

LogCleanupPostInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class LogCleanupPostInput(ValidatorModel):
       retention_days: int = Field(ge=90)
       batch_size: int = 10000

LogCleanupPostOutput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class LogCleanupPostOutput(ValidatorModel):
       total_pipeline_executions_deleted: int = Field(ge=0)
       total_timeliness_pipeline_execution_logs_deleted: int = Field(ge=0)
       total_anomaly_detection_results_deleted: int = Field(ge=0)
       total_pipeline_execution_closure_parent_deleted: int = Field(ge=0)
       total_pipeline_execution_closure_child_deleted: int = Field(ge=0)
       total_freshness_pipeline_logs_deleted: int = Field(ge=0)

Enums
-----

AnomalyMetricFieldEnum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class AnomalyMetricFieldEnum(str, Enum):
       TOTAL_ROWS = "total_rows"
       DURATION_SECONDS = "duration_seconds"
       THROUGHPUT = "throughput"
       INSERTS = "inserts"
       UPDATES = "updates"
       SOFT_DELETES = "soft_deletes"

DatePartEnum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class DatePartEnum(str, Enum):
       HOUR = "hour"
       DAY = "day"
       WEEK = "week"
       MONTH = "month"
       QUARTER = "quarter"
       YEAR = "year"

ValidatorModel
--------------

All models inherit from ``ValidatorModel`` which provides:

- **Pydantic validation** Automatic data validation and type checking
- **String coercion** Automatic conversion of various types for watermarks to strings for database storage
- **Case normalization** Automatic lowercase conversion for string fields
- **Field validation** Built-in validation for field constraints (length, ranges, etc.)

Example:

.. code-block:: python

   from src.types import ValidatorModel
   from pydantic import Field
   from typing import Optional

   class MyModel(ValidatorModel):
       name: str = Field(max_length=150, min_length=1)
       value: Optional[int] = Field(None, ge=0)
       created_at: Optional[DateTime] = None

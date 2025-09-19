# Watcher
**Open Source Metadata Framework for Data Engineers**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness & freshness of data, detect anomalies among operations, manage data addresses, and provide observability across your data infrastructure.

![Watcher](watcher.jpg)

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

## Table of Contents

1. [Features](#features)
2. [API Endpoints](#-api-endpoints)
3. [Database Schema](#️-database-schema)
4. [Technology Stack](#️-technology-stack)
   - [Configuration](#configuration)
5. [Recommended Organization](#-recommended-organization)
6. [Nested Pipeline Executions](#-nested-pipeline-executions)
7. [Timeliness & Freshness](#-timeliness--freshness)
8. [Anomaly Checks](#-anomaly-checks)
9. [Log Cleanup](#-log-cleanup--maintenance)
10. [Complete Pipeline Workflow Example](#complete-pipeline-workflow-example)
11. [Development](#️-development)
    - [Development Setup](#development-setup)
    - [Performance Profiling](#performance-profiling)

## Features

### 🔄 Pipeline Execution Monitoring
- **Execution Tracking**: Start and end pipeline executions with detailed metadata to track performance
- **Performance Metrics**: Track duration, DML counts (inserts, updates, deletes), and total rows processed
- **Execution History**: Maintain complete audit trail of all pipeline runs
- **Status Management**: Monitor active/inactive pipeline states
- **Nested Executions**: Support for hierarchical pipeline execution tracking using parent_id

### ⏰ Timeliness & Freshness Checks
- **Pipeline Execution Timeliness**: Monitor if pipeline executions complete within expected timeframes
- **DML Freshness Monitoring**: Check if data manipulation operations (inserts, updates, deletes) are recent enough
- **Configurable Thresholds**: Set custom rules per pipeline type and individual pipelines
- **Mute Capability**: Skip checks for specific pipelines when needed

*See [Timeliness & Freshness](#-timeliness--freshness) section for detailed configuration and usage.*

### 🔗 Data Lineage Tracking
- **Address Management**: Track source and target data addresses with type classification
- **Lineage Relationships**: Create and maintain data flow relationships between sources and targets
- **Closure Table Pattern**: Efficient querying of complex lineage hierarchies with depth tracking
- **Source Control Integration**: Store lineage definitions in version control for reproducibility

### 💧 Watermark Management
- **Incremental Processing**: Support for watermark-based incremental data pipelines
- **Flexible Watermarking**: Use any identifier (IDs, timestamps, etc.) as watermarks
- **Automatic Updates**: Watermarks are automatically updated after successful pipeline execution

### 📊 Metadata Storage
- **Pipeline Configuration**: Store pipeline arguments and configuration as JSONB
- **Type Classification**: Organize pipelines by type for better management and control
- **Address Type System**: Categorize data sources and targets by type and group

### 🚨 Anomaly Detection
- **Statistical Analysis**: Detect anomalies using standard deviation and z-score analysis
- **Configurable Metrics**: Monitor duration, row counts, and DML operations for individual pipelines
- **Automatic Detection**: Run anomaly detection automatically after pipeline execution
- **Confidence Scoring**: Calculate confidence scores based on statistical deviation
- **Lookback Periods**: Analyze historical data over configurable time windows
- **Auto-Create Rules**: Automatically create default anomaly detection rules for new pipelines

*See [Anomaly Checks](#-anomaly-checks) section for detailed configuration and usage.*

### 🧹 Log Cleanup
- **Automated Maintenance**: Remove old log data to maintain database performance
- **Batch Processing**: Safe deletion in configurable batches to avoid database locks
- **Cascading Cleanup**: Maintains referential integrity across related tables
- **Configurable Retention**: Set custom retention periods for different data types

*See [Log Cleanup & Maintenance](#-log-cleanup--maintenance) section for detailed configuration and usage.*

### 🔧 Development & Operations
- **RESTful API**: Complete REST API for all operations with automatic documentation
- **Database Migrations**: Alembic-based migration system for schema evolution
- **Testing Framework**: Comprehensive test suite with fixtures and async support
- **Docker Support**: Containerized deployment with Docker
- **Logging & Observability**: Structured logging with Logfire integration


## 📋 API Endpoints

### Pipeline Management
- `POST /pipeline` - Create or get existing pipeline
- `GET /pipeline` - List all pipelines
- `PATCH /pipeline` - Update pipeline configuration

### Pipeline Execution
- `POST /start_pipeline_execution` - Start a new pipeline execution
- `POST /end_pipeline_execution` - End a pipeline execution with metrics

### Pipeline Types
- `POST /pipeline_type` - Create or get pipeline type
- `GET /pipeline_type` - List all pipeline types

### Address Management
- `POST /address` - Create or get address
- `GET /address` - List all addresses
- `PATCH /address` - Update address information

### Address Types
- `POST /address_type` - Create or get address type
- `GET /address_type` - List all address types

### Data Lineage
- `POST /address_lineage` - Create lineage relationships between addresses
- `GET /address_lineage/{address_id}` - Get lineage for specific address

### Anomaly Detection
- `POST /anomaly_detection_rule` - Create or get anomaly detection rule
- `GET /anomaly_detection_rule` - List all anomaly detection rules
- `PATCH /anomaly_detection_rule` - Update anomaly detection rule
- `POST /anomaly_detection/detect/{pipeline_id}` - Run anomaly detection for a pipeline

*See [Anomaly Checks](#-anomaly-checks) section for detailed configuration and usage.*

### Monitoring & Health
- `POST /timeliness` - Check pipeline execution timeliness (requires `lookback_minutes` parameter)
- `POST /freshness` - Check DML operation freshness
- `POST /log_cleanup` - Clean up old log data
- `GET /celery/monitoring` - Real-time Celery worker monitoring dashboard
- `GET /` - Health check endpoint
- `GET /scalar` - Interactive API documentation (utilizes Scalar for an intuitive interface to explore and test all available endpoints)

## 🗄️ Database Schema

### Core Tables
- **`pipeline`** - Pipeline definitions with configuration and metadata
- **`pipeline_type`** - Pipeline type definitions and broad timeliness & freshness rules
- **`pipeline_execution`** - Individual pipeline execution records and metrics
- **`address`** - Data address definitions (databases, files, APIs, etc.)
- **`address_type`** - Address type categorization
- **`address_lineage`** - Source-to-target data lineage relationships
- **`address_lineage_closure`** - Optimized closure table for efficient lineage queries
- **`timeliness_pipeline_execution_log`** - Log of pipeline executions that have exceeded timeliness thresholds
- **`freshness_pipeline_log`** - Log of pipelines that have failed freshness checks
- **`anomaly_detection_rule`** - Anomaly detection rules and configuration per pipeline
- **`anomaly_detection_result`** - Detected anomalies with statistical analysis and confidence scores

### Database Key Features
- **PostgreSQL JSONB** for flexible configuration storage
- **Timezone-aware timestamps** for all datetime fields
- **Optimized indexes** for performance-critical queries
- **Foreign key constraints** for data integrity
- **Closure table pattern** for efficient lineage traversal

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and settings management using Python type annotations
- **SQLModel** - SQL databases in Python, designed for simplicity and compatibility
- **PostgreSQL** - Robust relational database with JSONB support
- **Alembic** - Database migration tool for SQLAlchemy
- **AsyncPG** - Async PostgreSQL driver
- **HTTPX** - Async HTTP client for external API calls (Slack)
- **Pendulum** - Better dates and times for Python

### Development & Testing
- **Pytest** - Testing framework with async support
- **Ruff** - Fast Python linter and formatter
- **Pre-commit** - Git hooks for code quality
- **UV** - Fast Python package manager
- **Scalar** - Interactive API documentation

### Logging & Observability
- **Logfire** - Comprehensive structured logging and observability platform
  - **Application Logs**: FastAPI request/response logging with automatic instrumentation
  - **Database Logs**: SQLAlchemy query logging and performance monitoring
  - **Background Tasks**: Celery worker execution logging and task tracking
  - **Structured Data**: JSON-formatted logs with consistent metadata across all components
  - **Logical Grouping**: Logs organized by operation type (API, Database, Background Tasks)
  - **Performance Insights**: Automatic timing and performance metrics collection
  - **Error Tracking**: Detailed error context and stack traces with correlation IDs

### Infrastructure
- **Docker** - Containerization
- **Uvicorn** - ASGI server for FastAPI
- **Gunicorn** - WSGI server to handle mutliple Uvicorn workers
- **Celery** - Distributed task queue for background processing
- **Redis** - Message broker and result backend for Celery

### Configuration

Watcher supports various configuration options through environment variables. The system uses different prefixes for different environments:

- **Development**: `DEV_` prefix
- **Production**: `PROD_` prefix  
- **Testing**: `TEST_` prefix

#### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `None` | Yes |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | `None` | No |
| `LOGFIRE_TOKEN` | Logfire token for logging | `None` | No |
| `WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES` | Auto-create all anomaly detection rules for new pipelines | `False` | No |

**Example Configuration:**
```bash
# Development environment
DEV_DATABASE_URL=postgresql://user:password@localhost:5432/watcher_dev
DEV_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DEV_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true

# Production environment  
PROD_DATABASE_URL=postgresql://user:password@prod-db:5432/watcher_prod
PROD_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=false
```

**Note**: When auto-creation is enabled, default anomaly detection rules are created with standard thresholds. You may want to customize these rules after creation based on your specific pipeline patterns and requirements. *See [Auto-Create Anomaly Detection Rules](#auto-create-anomaly-detection-rules) section for details.*

## 📋 Recommended Organization

Effective organization of your Watcher metadata is crucial for maintainability, monitoring, and team collaboration. This section provides recommended naming conventions and organizational patterns.

### Best Practices

1. **Consistency**: Use the same naming patterns across all teams and projects
2. **Descriptiveness**: Names should clearly indicate purpose and scope
3. **Hierarchy**: Use underscores to create logical hierarchies
4. **Future-Proofing**: Choose names that will remain relevant as systems evolve
5. **Documentation**: Document your naming conventions and share with all teams
6. **Validation**: Implement naming validation in your CI/CD pipeline or code reviews

### Pipeline Type Organization

Organize pipeline types by data processing patterns or business domains or a combination of both:

Data Processing Pattern:  
- `extraction` - Data extraction pipelines
- `transformation` - Data transformation and processing
- `loading` - Data loading and materialization
- `audit` - Data quality and validation
- `monitoring` - System monitoring and health checks  

Organize pipeline types by business domain:  
- `sales`
- `marketing`
- `finance` 

A combination of both:  
- `sales_extraction`
- `marketing_audit`
- `finance_monitoring`

### Pipeline Naming Convention

Use a clear naming structure that matches back to the pipeline code (e.g., DAG name, job name, or workflow identifier). 

**Best Practices:**
- Match your DAG/job/workflow names exactly
- Use consistent abbreviations across your organization
- Keep names descriptive but concise
- Use underscores for separation, avoid special characters

### Address Type Organization

Categorize addresses by their technical characteristics:

**Group Names:**
- `database` - Database systems (PostgreSQL, MySQL, etc.)
- `warehouse` - Data warehouses (Snowflake, BigQuery, etc.)
- `bucket` - Data lakes (S3, ADLS, etc.)
- `api` - API endpoints and services
- `file` - File systems and storage
- `stream` - Streaming data sources

**Type Names:**
- `postgresql` - PostgreSQL databases
- `snowflake` - Snowflake data warehouse
- `s3` - Amazon S3 storage
- `rest_api` - REST API endpoints
- `kafka` - Kafka streaming platform

### Address Naming Convention

Addresses should be the actual, usable path/URL that you would use to access the data:

**Examples:**
- `gs://my-bucket/raw/events/2024/01/09/` - GCS bucket path for raw events
- `https://api.example.com/v1/customers` - REST API endpoint for customers
- `analytics.public.users` - database table
- `topic-name` - Kafka topic with broker info

**Best Practices:**
- Use the URL format for the system
- Be specific enough that someone could use the address to access the data given the address type context
- Use standard formats for each system type (Bucket URLs, HTTP endpoints, database.schema.table)

## 🔗 Nested Pipeline Executions

Watcher supports hierarchical pipeline execution tracking through the `parent_id` field, enabling you to model complex workflows with sub-pipelines and dependencies:

**Use Cases:**
- **Master Pipeline**: A main orchestration pipeline that coordinates multiple sub-pipelines
- **Sub-Pipeline Tracking**: Individual components or steps within a larger workflow
- **Dependency Management**: Track which sub-pipelines depend on others
- **Performance Analysis**: Analyze execution times at both master and sub-pipeline levels
- **Error Isolation**: Identify which specific sub-pipeline failed within a complex workflow

**Example Workflow:**
```
Master Pipeline: data_processing_master
├── Sub-Pipeline: extract_sales_data (parent_id: master_execution_id)
├── Sub-Pipeline: extract_marketing_data (parent_id: master_execution_id)
├── Sub-Pipeline: transform_combined_data (parent_id: master_execution_id)
└── Sub-Pipeline: load_to_warehouse (parent_id: master_execution_id)
```

**API Usage:**
```python
# Start master pipeline execution
master_response = await client.post("/start_pipeline_execution", json={
    "pipeline_name": "data_processing_master"
})
master_execution_id = master_response.json()["id"]

# Start sub-pipeline execution with parent reference
sub_response = await client.post("/start_pipeline_execution", json={
    "pipeline_name": "extract_sales_data",
    "parent_id": master_execution_id
})
```

**Benefits:**
- **Hierarchical Monitoring**: Track both overall workflow progress and individual component performance
- **Dependency Tracking**: Understand which sub-pipelines are blocking others
- **Root Cause Analysis**: Quickly identify which specific component caused a failure
- **Resource Optimization**: Analyze which sub-pipelines consume the most time/resources
- **Audit Trail**: Complete visibility into complex multi-step data processes

## ⏰ Timeliness & Freshness

The monitoring system provides two complementary checks, timeliness & freshness, to ensure your data pipelines are running optimally. They run through the two endpoints: `freshness` and `timeliness`. Ping these endpoints on a regular cadence to have constant broad coverage. These endpoints queue background tasks using Celery workers to lessen the impact on the server.

### Pipeline Execution Timeliness
Monitors if pipeline executions complete within expected timeframes, helping identify performance issues and long-running processes. Uses a configurable lookback window to check executions (running and completed).

#### Timeliness Check Features
- **Lookback Window**: Configurable time window to check for overdue executions (e.g., any execution started within the last 60 minutes)
- **Running Pipeline Detection**: Identifies currently running pipelines that exceed their threshold
- **Completed Pipeline Detection**: Identifies completed pipelines that took longer than expected
- **Dynamic Thresholds**: Uses pipeline-specific or pipeline-type-specific timeliness settings


### Pipeline Freshness (DML Monitoring)
Checks if data manipulation operations (inserts, updates, deletes) are recent enough, ensuring data freshness for downstream consumers.

#### Freshness Check Features
- **DML Operation Tracking**: Monitors insert, update, and soft delete timestamps (calculated behind the scenes from completed pipeline execution data)
- **Configurable Thresholds**: Set freshness rules per pipeline type and individual pipelines
- **Recent Activity Detection**: Identifies pipelines with stale data based on last DML operations
- **Flexible Time Units**: Support for hours, days, or other time units for freshness rules
- **Mute Capability**: Skip freshness checks for specific pipelines when needed

### Configuration

Timeliness & Freshness rules can be set at two levels:

#### Pipeline Type Level (Parent Rules)
Set broad timeliness rules that apply to all pipelines of a specific type:

```python
pipeline_type_data = {
    "name": "api-integration",
    "freshness_number": 12,
    "freshness_datepart": "hour",
    "mute_freshness_check": False,
    "timeliness_number": 30,
    "timeliness_datepart": "minute",
    "mute_timeliness_check": False
}
```

#### Pipeline Level (Child Rules)
Override parent rules with pipeline-specific settings:

```python
pipeline_data = {
    "name": "critical-data-pipeline",
    "freshness_number": 2,
    "freshness_datepart": "hour",
    "mute_freshness_check": False,
    "timeliness_number": 15,
    "timeliness_datepart": "minute",
    "mute_timeliness_check": False
}
```

### Supported Time Units

The monitoring system supports granular time windows for flexible monitoring configurations. You can set any combination of time unit and number to create precise timeliness rules:

- **MINUTE** - Within N minutes (e.g., 5 minutes, 30 minutes)
- **HOUR** - Within N hours (e.g., 1 hour, 6 hours, 12 hours)  
- **DAY** - Within N days (e.g., 1 day, 3 days, 7 days)
- **WEEK** - Within N weeks (e.g., 1 week, 2 weeks, 4 weeks)
- **MONTH** - Within N months (e.g., 1 month, 3 months, 6 months)
- **YEAR** - Within N years (e.g., 1 year, 2 years)

### Priority System

1. **Child Rules** - Pipeline-specific settings take precedence
2. **Parent Rules** - Fall back to pipeline type settings
3. **Skip** - If neither child nor parent rules are configured, the pipeline is skipped

### Slack Notifications

The system sends comprehensive Slack notifications for various monitoring issues:

#### DML Freshness Failures
When pipelines fail their freshness checks, detailed Slack notifications are sent including:

- **Pipeline Information**: Pipeline name, ID, and last DML timestamp
- **DML Timestamps**: Last insert, update, and soft delete timestamps
- **Expected Timeframe**: Configured freshness rules and thresholds
- **Overdue Details**: Specific duration beyond expected timeframe

Example notification:
```
⚠️ WARNING
Timestamp: 2025-01-09 20:30:45 UTC
Message: Pipeline Freshness Check Failed - 2 pipeline(s) overdue

Details:
• Failed Pipelines:
  • stock-price-worker (ID: 1): Last DML 2025-01-09 15:30:00, Expected within 12 hours
  • user-analytics-pipeline (ID: 2): Last DML 2025-01-09 10:15:00, Expected within 6 hours
```

#### Pipeline Execution Timeliness Failures
When pipeline executions exceed their timeliness threshold, notifications include:

- **Execution Details**: Pipeline execution ID, duration, and affected pipeline name
- **Execution Status**: Whether the pipeline is currently running or completed
- **Threshold Information**: Configured threshold and actual execution time
- **Configuration Source**: Whether the threshold comes from pipeline-specific or pipeline-type settings

Example notification:
```
⚠️ WARNING
Timestamp: 2025-01-09 20:30:45 UTC
Message: Pipeline Execution Timeliness Check Failed - 2 execution(s) overdue

Details:
• Failed Executions:
  • Pipeline Execution ID: 456 (Pipeline ID: 1): 3621 seconds (running), Expected within 30 minutes (child config)
  • Pipeline Execution ID: 457 (Pipeline ID: 2): 2415 seconds (completed), Expected within 15 minutes (parent config)
```

### API Usage

#### Pipeline Execution Timeliness
```python
# Check pipeline execution timeliness with lookback window
timeliness_data = {
    "lookback_minutes": 60  # Check executions from the last 60 minutes
}

response = await client.post("http://localhost:8000/timeliness", json=timeliness_data)
result = response.json()

if result["status"] == "queued":
    print("Timeliness check has been queued for background processing")
    print("Check Slack notifications for detailed results when processing completes")
else:
    print(f"Unexpected status: {result['status']}")
```

#### DML Freshness Monitoring
```python
# Check DML operation freshness
response = await client.post("http://localhost:8000/freshness")
result = response.json()

if result["status"] == "queued":
    print("Freshness check has been queued for background processing")
    print("Check Slack notifications for detailed results when processing completes")
else:
    print(f"Unexpected status: {result['status']}")
```

#### Response Status Codes

- **200 OK**: Timeliness check queued successfully
  - `{"status": "queued"}` - Check has been queued for background processing by Celery workers

#### Input Parameters

- **`lookback_minutes`** (required): Time window in minutes to check for overdue executions
  - Example: `60` - Check executions from the last 60 minutes
  - Example: `1440` - Check executions from the last 24 hours
  - Example: `10080` - Check executions from the last week

#### Monitoring Integration
- **Real-time Alerts**: Immediate Slack notifications for urgent issues
- **Historical Tracking**: All timeliness & freshness issues are logged to the database
- **Lookback Filtering**: Notifications only alert on new executions within the current lookback range
- **Issue Context**: Clear identification of which specific pipelines/executions had issues

## 🚨 Anomaly Checks

The anomaly detection system provides statistical analysis to identify unusual patterns in pipeline execution metrics, helping you quickly spot performance issues and data quality problems.

### How It Works

Anomaly detection uses statistical methods to analyze historical pipeline execution data and identify outliers:

1. **Baseline Calculation**: Analyzes historical execution data over a configurable lookback period for the same hour of day to account for seasonality
2. **Statistical Analysis**: Uses standard deviation and z-score calculations to determine normal ranges
3. **Threshold Detection**: Flags executions that exceed configurable statistical thresholds
4. **Confidence Scoring**: Provides confidence scores based on how far outside normal ranges the execution falls

### Configuration

#### Rule Creation
Create anomaly detection rules per pipeline with the following parameters:

- **`pipeline_id`**: Target pipeline to monitor
- **`metric_field`**: Metric to monitor (duration_seconds, total_rows, total_inserts, etc.)
- **`lookback_days`**: Number of days of historical data to analyze (default: 30)
- **`minimum_executions`**: Minimum executions needed for baseline calculation (default: 10)
- **`std_deviation_threshold_multiplier`**: How many standard deviations above mean to trigger (default: 2.0)
- **`active`**: Whether the rule is enabled

#### Supported Metrics

The system can monitor various execution metrics:

- **`duration_seconds`**: Pipeline execution duration
- **`total_rows`**: Total rows processed
- **`total_inserts`**: Number of insert operations
- **`total_updates`**: Number of update operations
- **`total_soft_deletes`**: Number of soft delete operations

### Automatic Detection

Anomaly detection runs automatically after each successful pipeline execution using Celery background workers:

1. **Trigger**: Queues when `end_pipeline_execution` is called and the execution was successful
2. **Background Processing**: Celery worker picks up the task
3. **Rule Lookup**: Finds active rules for the completed pipeline
4. **Historical Analysis**: Analyzes execution history for the same hour of day
5. **Statistical Calculation**: Computes baseline mean and standard deviation
6. **Anomaly Detection**: Identifies executions exceeding thresholds
7. **Notification**: Sends Slack alerts for detected anomalies

### Slack Notifications

When anomalies are detected, the system sends detailed Slack notifications:

```
⚠️ WARNING
Anomaly Detection
Timestamp: 2025-01-09 20:30:45 UTC
Message: Anomaly detected in pipeline 123 - 2 execution(s) flagged

Details:
• Metric: duration_seconds
• Threshold Multiplier: 2.0
• Lookback Days: 30
• Anomalies: 
  - Execution ID 21: 1814400 (baseline: 164945.45, deviation: 1000.0%, confidence: 1.00)
  - Execution ID 22: 1952000 (baseline: 164945.45, deviation: 1083.3%, confidence: 0.99)
```

#### Auto-Create Anomaly Detection Rules

When the `WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES` environment variable is set to `true`, the system automatically creates anomaly detection rules for all available metrics when a new pipeline is created. This includes rules for:

- **Duration Monitoring**: `duration_seconds` - Tracks pipeline execution time
- **DML Operations**: `inserts`, `updates`, `soft_deletes` - Monitors data modification counts
- **Volume Monitoring**: `total_rows` - Tracks total rows processed

**Default Rule Settings:**
- **Standard Deviation Threshold**: `2.0` (flags values 2+ standard deviations from mean)
- **Lookback Period**: `30 days` (analyzes historical data over 30 days)
- **Minimum Executions**: `10` (requires at least 10 historical executions for analysis)
- **Active by Default**: `true` (rules are enabled immediately)

### Best Practices

1. **Start Conservative**: Begin with higher threshold multipliers (2.5-3.0) and adjust based on your data patterns
2. **Monitor Multiple Metrics**: Create rules for different metrics to get comprehensive coverage
3. **Regular Review**: Periodically review and adjust rules based on changing data patterns
4. **Sufficient History**: Ensure you have enough historical data for accurate baseline calculations 
5. **Hour-Specific Analysis**: The system analyzes data by hour of day, so consider time-of-day patterns

## 🧹 Log Cleanup & Maintenance

The log cleanup system provides automated maintenance for historical data, helping you manage database growth and maintain optimal performance by removing old log records while preserving recent data for analysis and monitoring.

### How It Works

The log cleanup system identifies and removes old records from log tables based on a configurable retention period:

1. **Retention Calculation**: Calculates a cutoff date based on current date minus retention days
2. **Batch Processing**: Deletes records in configurable batches to avoid database locks
3. **Cascading Cleanup**: Removes related records from dependent tables in the correct order
4. **Progress Tracking**: Reports the number of records deleted from each table

### Configuration

#### Input Parameters

- **`retention_days`**: Number of days to retain data (minimum: 90 days)
- **`batch_size`**: Number of records to delete per batch (default: 10,000)

#### Example Request

```python
cleanup_data = {
    "retention_days": 90,
    "batch_size": 5000
}

response = await client.post("http://localhost:8000/log_cleanup", json=cleanup_data)
result = response.json()
```

### Cleanup Process

The system cleans up data from four main log tables in a specific order to maintain referential integrity:

#### 1. Freshness Pipeline Logs
- **Table**: `freshness_pipeline_log`
- **Filter**: Records with `last_dml_timestamp <= retention_date`
- **Purpose**: Removes old DML freshness check logs

#### 2. Timeliness Pipeline Execution Logs
- **Table**: `timeliness_pipeline_execution_log`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old timeliness check logs

#### 3. Anomaly Detection Results
- **Table**: `anomaly_detection_result`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old anomaly detection results

#### 4. Pipeline Executions (Last)
- **Table**: `pipeline_execution`
- **Filter**: Records with `id <= max_pipeline_execution_id`
- **Purpose**: Removes old pipeline execution records (must be last due to foreign key constraints)

### Best Practices

1. **Regular Cleanup**: Schedule cleanup operations regularly (e.g., weekly or monthly)
2. **Conservative Retention**: Start with longer retention periods and adjust based on your needs
3. **Batch Size**: Use appropriate batch sizes based on your database performance

### Safety Features

- **Minimum Retention**: Enforces a minimum 90-day retention period
- **Batch Processing**: Prevents database locks and memory issues
- **Cascading Deletes**: Maintains referential integrity by cleaning dependent tables
- **Progress Tracking**: Provides visibility into cleanup operations
- **Graceful Handling**: Stops processing when no more records are found

This log cleanup system helps maintain optimal database performance while preserving the data you need for monitoring and analysis.

## Complete Pipeline Workflow Example
```python
import httpx
import asyncio
import pendulum

async def run_pipeline_workflow():
    """Complete example of creating and running a pipeline with lineage tracking"""

    # Grab our upper bound next watermark
    # This would be: SELECT MAX(id) FROM your_table or whatever you're working with
    max_id_from_source = 150

    # Step 1: Create Pipeline Record
    # If Pipeline exists, an id is returned anyway
    pipeline_data = {
        "name": "stock-price-worker",
        "pipeline_type_name": "api-integration",
        "full_load": False,
        "next_watermark": max_id_from_source  # Converted to string
    }
    try:
        async with httpx.AsyncClient() as client:
            # Create the pipeline
            pipeline_response = await client.post("http://localhost:8000/pipeline", json=pipeline_data)
            pipeline_result = pipeline_response.json()
            
            print(f"Pipeline ID: {pipeline_result['id']}")
            print(f"Active: {pipeline_result['active']}")
            print(f"Load Lineage: {pipeline_result['load_lineage']}")
            print(f"Watermark: {pipeline_result}['watermark']")
            
            # Step 2: Check if pipeline is active
            # Programmatic way to control pipelines for flexibility
            if not pipeline_result['active']:
                print("Pipeline is not active. Exiting...")
                return
            
            # Step 3: If load_lineage is true, create address lineage relationships
            # This forces lineage data to be in source control and only reloads if necessary
            # Can set manually through API, once execution is complete defaults back to False
            if pipeline_result['load_lineage']:
                lineage_data = {
                    "pipeline_id": pipeline_result['id'],
                    "source_addresses": [
                        {
                            "address_name": "source_db.stock_prices",
                            "address_type_name": "postgresql",
                            "address_type_group_name": "database"
                        }
                    ],
                    "target_addresses": [
                        {
                            "address_name": "warehouse.stock_prices",
                            "address_type_name": "postgresql",
                            "address_type_group_name": "database"
                        }
                    ]
                }
                
                lineage_response = await client.post("http://localhost:8000/address_lineage", json=lineage_data)
                lineage_result = lineage_response.json()
                print(f"Lineage relationships created: {lineage_result['lineage_relationships_created']}")
            
            # Step 4: Start Pipeline Execution
            execution_start_data = {
                "pipeline_id": pipeline_result['id'],
                "start_date": pendulum.now("UTC").isoformat()
            }
            
            start_response = await client.post("http://localhost:8000/start_pipeline_execution", json=execution_start_data)
            execution_id = start_response.json()['id']
            
            print(f"Pipeline execution associated with ID: {execution_id}")

            # Utilize watermarks
            next_watermark = max_id_from_source
            watermark = int(pipeline_result['watermark'])
            
            # Step 5: Incremental Data Pipeline (utilizing watermarks)
            # ...
            SELECT
            *
            FROM Table_A
            WHERE id <= next_watermark
                AND id > watermark
            # ...
            
            # Step 6: End Pipeline Execution (with DML counts gathered from work)
            execution_end_data = {
                "id": execution_id,
                "end_date": pendulum.now("UTC").isoformat(),
                "completed_successfully": True,
                "inserts": 150,
                "updates": 25,
                "soft_deletes": 5,
                "total_rows": 180,
                "execution_metadata": {
                    "partition": ...
                }
            }
            
            # Ending execution automatically increments watermark to next_watermark
            # Also automatically sets load_lineage back to False to avoid excess calls
            await client.post("http://localhost:8000/end_pipeline_execution", json=execution_end_data)
            print("Pipeline execution completed successfully")
        except Exception as e:
            execution_end_data = {
                "id": execution_id,
                "end_date": pendulum.now("UTC").isoformat(),
                "completed_successfully": False,
                "execution_metadata": {
                    "error": ...
                }
            }
            
            # Alerting
            ...

if __name__ == "__main__":
    asyncio.run(run_pipeline_workflow())
```

## 🛠️ Development

### Development Setup
1. Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Install python 3.12
```bash
uv python install 3.12
```
3. Check installation
```bash
uv python list
```
4. Sync python packages
```bash
uv sync
```
5. Add in pre-commits (you might need to run `source .venv/bin/activate` if your uv environment is not being recognized)
```bash
pre-commit install
pre-commit install --hook-type pre-push
```
6. Add in Environment Variables referencing `.env.example`

### Quick Start
```bash
# Start the development server
make start

# Run tests
make test

# Format and lint code
make format
```

### Database Management
```bash
# Add a new migration
make add-migration msg="description of changes"

# Apply migrations
make trigger-migration
```

### Performance Profiling

Watcher includes built-in performance profiling for development using pyinstrument to help identify bottlenecks and optimize your pipeline operations.

#### On-Demand Profiling

Profile any API endpoint by adding `?profile=true` to the URL:

#### Using Scalar API Docs

1. **Start your app**: `make start`
2. **Open Scalar**: http://localhost:8000/scalar
3. **Add `?profile=true`** as a query parameter to any endpoint URL in the interface
4. **Execute the request** - you'll get an interactive HTML profile directly in your browser

#### Profile Features

- **Interactive Call Stack**: Click to expand/collapse function calls
- **Timing Breakdown**: See exactly where time is spent
- **Database Operations**: Identify slow queries and connection issues
- **Memory Usage**: Track memory allocation patterns
- **Search & Filter**: Find specific functions or modules

#### Configuration

Profiling is enabled by default in development mode. To disable:

```bash
# Set in your environment
DEV_PROFILING_ENABLED=false
```

### Development Workflow
1. **Adding New Tables**: Add model to `src.database.models.__init__.py` for SQLModel metadata
2. **Database Migrations**: Use `make add-migration` to generate migration scripts
3. **Testing**: Use `make test` to run the comprehensive test suite
4. **Code Quality**: Pre-commit hooks automatically format and lint code
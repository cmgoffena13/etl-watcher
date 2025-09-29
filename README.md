# Watcher
**Open Source Metadata Framework for Data Engineers**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness & freshness of data, detect anomalies among operations, manage data addresses, and provide observability across your data infrastructure.

![Watcher](watcher.jpg)

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

## Table of Contents

1. [Features](#features)
2. [API Endpoints](#-api-endpoints)
3. [Webpages](#-webpages)
4. [Database Schema](#️-database-schema)
   - [Custom Querying](#custom-querying)
5. [Technology Stack](#️-technology-stack)
   - [Configuration](#configuration)
6. [Celery Background Processing](#-celery-background-processing)
7. [Recommended Organization](#-recommended-organization)
8. [Nested Pipeline Executions](#-nested-pipeline-executions)
9. [Timeliness & Freshness](#-timeliness--freshness)
10. [Anomaly Checks](#-anomaly-checks)
    - [Adjusting Thresholds](#adjusting-thresholds)
11. [Log Cleanup](#-log-cleanup--maintenance)
12. [Complete Pipeline Workflow Example](#complete-pipeline-workflow-example)
13. [Development](#️-development)
    - [Development Setup](#development-setup)
    - [Performance Profiling](#performance-profiling)
    - [Load Testing](#load-testing)
14. [Deployment](#-deployment)

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
- **Statistical Analysis**: Analyze individual pipeline executions against historical baselines using standard deviation and z-score analysis
- **Configurable Metrics**: Monitor duration, row counts, and DML operations for individual pipelines
- **Automatic Detection**: Run anomaly detection automatically after each pipeline execution
- **Historical Baselines**: Calculate statistical baselines from historical execution data over configurable time windows
- **Single Execution Analysis**: Compare each pipeline execution against its calculated statistical baseline
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
- `POST /celery/monitor-queue` - Trigger Celery queue monitoring and alerting (see [Celery Background Processing](#-celery-background-processing) for details)
- `GET /` - Health check endpoint
- `GET /scalar` - Interactive API documentation (utilizes Scalar for an intuitive interface to explore and test all available endpoints)

## 🌐 Webpages

### Diagnostics Dashboard
- `GET /diagnostics` - Interactive database diagnostics dashboard
  - **Connection Speed Test** - Raw asyncpg connection performance testing
  - **Connection Performance** - Comprehensive connection scenarios (raw asyncpg, SQLAlchemy engine, pool behavior, DNS resolution)
  - **Schema Health Check** - Database schema analysis including:
    - Table sizes and row counts
    - Index usage statistics and performance metrics
    - Potential missing indexes for tables with sequential scans
    - Unused indexes identification
    - Table statistics and dead tuple analysis
  - **Performance & Locks** - Database performance monitoring including:
    - Deadlock statistics and trends
    - Currently locked tables (public schema only)
    - Top active queries with duration and wait events
    - Long running queries (>30s) identification


### Pipeline Reporting Dashboard
- `GET /reporting` - Daily pipeline metrics and performance analytics dashboard
  - **Pipeline Metrics** - Daily aggregations of execution counts, error rates, and performance data
  - **Pipeline Type Filtering** - Filter metrics by pipeline type (e.g., extraction, audit, sales)
  - **Pipeline Name Filtering** - Filter metrics by specific pipeline names
  - **Time Range Filtering** - View metrics for the last 1-30 days
  - **Performance Analytics** - Track throughput, duration, and DML operation trends
  - **Error Rate Monitoring** - Visual indicators for high, medium, and low error rates
  - **Pagination** - Navigate through large datasets with configurable page sizes
  - **Auto-Refresh** - Materialized view refreshes automatically on page load for fresh data
  - **Real-time Data** - Built on PostgreSQL materialized views for fast query performance
  
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
- **`anomaly_detection_result`** - Detected anomalies with statistical analysis and z-score data

### Database Key Features
- **PostgreSQL JSONB** for flexible configuration storage
- **Timezone-aware timestamps** for all datetime fields
- **Optimized indexes** for performance-critical queries
- **Foreign key constraints** for data integrity
- **Closure table pattern** for efficient lineage traversal

### Custom Querying
There is obviously the option of querying the database directly for investigative/reporting purposes. Main point of recommendation is be cautious when querying the `pipeline_execution` table as that will be the main target for DML operations. There is an index on `date_recorded, pipeline_id` that can be utilized by following this pattern:
```sql
with CTE AS (
    SELECT
    id
    FROM pipeline_execution
    WHERE pipeline_id = 1
        AND date_recorded >= CURRENT_DATE - INTERVAL '8 days'
        AND date_recorded < CURRENT_DATE  /* Stay away from current records being inserted/updated */
)
SELECT
pe.*  /* Columns you want to see */
FROM pipeline_execution AS pe
INNER JOIN CTE
    ON CTE.id = pe.id
```

If you are wanting to look at recent executions, you can utilize the index on `start_date` by utilizing the following pattern:
```sql
with CTE AS (
    SELECT
    id
    FROM pipeline_execution
    WHERE start_date >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
)
SELECT
pe.*  /* Columns you want to see */
FROM pipeline_execution pe
INNER JOIN CTE
    ON CTE.id = pe.id
```

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
DEV_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_dev
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_test
DEV_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DEV_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true

# Production environment  
PROD_DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/watcher_prod
PROD_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=false
PROD_LOGFIRE_TOKEN=12345/kjoi3rjasdfaeon
```

**Note**: When auto-creation is enabled, default anomaly detection rules are created with standard thresholds. You may want to customize these rules after creation based on your specific pipeline patterns and requirements. *See [Auto-Create Anomaly Detection Rules](#auto-create-anomaly-detection-rules) section for details.*

## 🔄 Celery Background Processing

Watcher uses Celery for distributed background task processing, providing reliable execution of monitoring checks, anomaly detection, and data processing tasks to make sure the main framework performs optimally. I recommend setting up a scheduled ping for the `celery/monitor-queue` endpoint every 5 minutes to have proper alerting on the Celery queue.

### Task Types
- **Anomaly Detection** - Statistical analysis of pipeline execution patterns
- **Freshness Checks** - DML operation monitoring and data staleness detection  
- **Timeliness Checks** - Pipeline execution timing validation
- **Log Cleanup** - Automated maintenance of historical data

### Queue Management
- **Default Queue** - All tasks are processed through the main queue
- **Worker Scaling** - Multiple workers can handle the same queue for load distribution
- **Task Retries** - Built-in retry logic with exponential backoff for failed tasks
- **Rate Limiting** - Configurable rate limits to prevent system overload

### Monitoring & Alerting
- **Task Tracking** - Individual task status and execution metrics
- **Performance Metrics** - Worker utilization and task processing rates
- **Diagnostics Page** - Comprehensive Celery worker and queue monitoring at `/diagnostics/celery`
  - Real-time worker status and activity
  - Queue depth monitoring
  - Task performance analytics with average duration by task type
  - Currently active tasks and worker activity summary

#### Alert Thresholds
- **INFO** (20+ messages): Queue is building up, monitor closely
- **WARNING** (50+ messages): Queue is getting backed up, consider scaling workers
- **CRITICAL** (100+ messages): Queue is severely backed up, immediate attention required

#### Example Alert Message
```
🚨 CRITICAL
Celery Queue Alert
Timestamp: 2025-09-28 06:04:26 UTC
Message: Queue has 2367 pending tasks

Details:
• Messages in queue: 2367
• Scheduled tasks: 0
• Total pending: 2367
```

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
- `dashboard` - dashboard targets

**Type Names:**
- `postgresql` - PostgreSQL databases
- `snowflake` - Snowflake data warehouse
- `s3` - Amazon S3 storage
- `rest_api` - REST API endpoints
- `kafka` - Kafka streaming platform
- `looker` - Looker dashboard

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
Message: Pipeline Freshness Check - 2 pipeline(s) overdue

Details:
• Failed Pipelines:
  • stock-price-worker (ID: 1): Last DML 2025-01-09 05:30:00, Expected within 12 hours
  • user-analytics-pipeline (ID: 2): Last DML 2025-01-09 08:15:00, Expected within 6 hours
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
Timestamp: 2025-09-28 01:14:37 UTC
Message: Pipeline Execution Timeliness Check - 2 new execution(s) overdue

Details:
• Failed Executions:
  • Pipeline 'hourly_pipeline_769' (Execution ID: 8374): 19.15 minutes (running), Expected within 15 minutes (child config)
  • Pipeline 'analytics_pipeline' (Execution ID: 8375): 40.25 minutes (completed), Expected within 30 minutes (parent config)
```

### API Usage

#### Pipeline Execution Timeliness
```python
# Check pipeline execution timeliness with lookback window
timeliness_data = {
    "lookback_minutes": 60  # Check executions that started within the last 60 minutes
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
  - Example: `60` - Check executions that started within the last 60 minutes
  - Example: `1440` - Check executions that started within the last 24 hours
  - Example: `10080` - Check executions that started within the last week

#### Monitoring Integration
- **Real-time Alerts**: Immediate Slack notifications for urgent issues
- **Historical Tracking**: All timeliness & freshness issues are logged to the database
- **Lookback Filtering**: Notifications only alert on new executions within the current lookback range
- **Issue Context**: Clear identification of which specific pipelines/executions had issues

## 🚨 Anomaly Checks

The anomaly detection system analyzes individual pipeline executions against statistical baselines calculated from historical execution data, helping you quickly spot performance issues and data quality problems.

1. **Historical Analysis**: Calculates statistical baselines (mean and standard deviation) from historical execution data for the same hour of day over a configurable lookback period
2. **Seasonality Adjustment**: Only uses executions from the same hour of day (e.g., 2 PM vs 2 PM) to account for daily patterns, business hours, and data processing cycles
3. **Statistical Baseline**: Uses standard deviation and z-score calculations to determine normal ranges from historical data
4. **Single Execution Analysis**: Compares the current pipeline execution against the calculated statistical baseline
5. **Z-Score Analysis**: Provides z-scores showing how many standard deviations the current execution deviates from the historical mean

### How It Works

Anomaly detection uses statistical methods to analyze one pipeline execution against statistical values calculated from historical execution data to identify whether it is an outlier. These are the components:

- **`Mean`** - the average of historical metric values from the same hour of day
- **`Standard Deviation`** - measures the spread/variability of historical values using sample standard deviation
- **`Z-Score`** - how many standard deviations the current value is from the historical mean
- **`Z-Threshold`** - sensitivity setting (e.g., 2.0 = flag anything beyond 2 standard deviations)
- **`Threshold Range`** - calculated bounds: `mean ± (std_dev * z_threshold)`

Below are the calculation steps:

1. **Gather Historical Data**: Collect executions within the lookback period and the same hour (excluding the current execution being analyzed)
2. **Calculate Statistical Baseline**: Compute the mean and standard deviation from the historical execution data for the metric
3. **Calculate Threshold Range**: Use the provided `z_threshold` and this formula:  
   `mean ± (std_dev * z_threshold)`
4. **Analyze Current Execution**: Compare the current pipeline execution's metric value against the calculated threshold range
5. **Flag Anomaly**: If the current execution's value is outside the threshold range (above upper bound or below lower bound), flag as an anomaly

### Automatic Detection Process

Anomaly detection runs automatically after each successful pipeline execution using Celery background workers:

1. **Trigger**: Queues when `end_pipeline_execution` is called and the execution was successful
2. **Background Processing**: Celery worker picks up the task
3. **Rule Lookup**: Finds active rules for the completed pipeline
4. **Process Execution**: Follows the calculation steps above to analyze the execution
5. **Notification**: Sends Slack alerts for detected anomalies

### Configuration

#### Rule Creation
Create anomaly detection rules per pipeline with the following parameters:

- **`pipeline_id`**: Target pipeline to monitor
- **`metric_field`**: Metric to monitor (duration_seconds, total_rows, total_inserts, etc.)
- **`lookback_days`**: Number of days of historical data to compare against execution (default: 30)
- **`minimum_executions`**: Minimum executions needed for baseline calculation (default: 10)
- **`z_threshold`**: How many standard deviations above mean to trigger (default: 2.0)
- **`active`**: Whether the rule is enabled

#### Supported Metrics

The system can monitor various execution metrics:

- **`duration_seconds`**: Pipeline execution duration
- **`total_rows`**: Total rows processed
- **`total_inserts`**: Number of insert operations
- **`total_updates`**: Number of update operations
- **`total_soft_deletes`**: Number of soft delete operations
- **`throughput`**: Total rows processed per second (automatically calculated)

### Slack Notifications

When anomalies are detected, the system sends detailed Slack notifications:

```
⚠️ WARNING
Anomaly Detection
Timestamp: 2025-01-09 20:30:45 UTC
Message: Anomaly detected in Pipeline 'analytics_pipeline' - Pipeline Execution ID 21 flagged

Details:
• Metric: duration_seconds
• Z-Threshold: 2.0
• Lookback Days: 30
• Minimum Executions: 10
• Anomaly:
    • Value: 4914 (Range: 0 - 4767)
```

#### Auto-Create Anomaly Detection Rules

When the `WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES` environment variable is set to `true`, the system automatically creates anomaly detection rules for all available metrics when a new pipeline is created. This includes rules for:

- **Duration Monitoring**: `duration_seconds` - Tracks pipeline execution time
- **DML Operations**: `inserts`, `updates`, `soft_deletes` - Monitors data modification counts
- **Volume Monitoring**: `total_rows` - Tracks total rows processed
- **Performance Monitoring**: `throughput` - Tracks total rows processed per second

**Default Rule Settings:**
- **Standard Deviation Threshold**: `2.0` (flags values 2+ standard deviations from mean)
- **Lookback Period**: `30 days` (analyzes execution against 30 days of historical data within the same hour)
- **Minimum Executions**: `10` (requires at least 10 historical executions for analysis)
- **Active by Default**: `true` (rules are enabled immediately)

### Adjusting Thresholds

The system provides detailed statistical data to help you fine-tune anomaly detection sensitivity. Each anomaly result includes both the **z-score** (actual deviation) and **z-threshold** (sensitivity setting) to guide adjustments.

#### Understanding the Data

**Z-Score vs Z-Threshold:**
- **Z-Score**: How many standard deviations the current value is from the historical mean
- **Z-Threshold**: Your sensitivity setting (e.g., 2.0 = flag anything beyond 2 standard deviations)
- **Relationship**: If `z_score > z_threshold` → Anomaly detected

#### Tuning Process
You are given the pipeline execution id in the alert message. You can utilize this to query the `anomaly_detection_result` table. Example below:

```sql
SELECT
/* Current Values */
adr.pipeline_execution_id,
rule.metric_field,
adr.violation_value,
adr.historical_mean,
adr.std_deviation_value,
adr.z_threshold,
adr.threshold_min_value,
adr.threshold_max_value,

/* Z-Score for analysis */
adr.z_score,
FLOOR(0, adr.historical_mean - (adr.std_deviation_value * adr.z_score)) AS new_threshold_min_value,
adr.historical_mean + (adr.std_deviation_value * adr.z_score) AS new_threshold_max_value
FROM public.anomaly_detection_result AS adr
INNER JOIN public.anomaly_detection_rule AS rule
    ON rule.id = adr.rule_id
WHERE pipeline_execution_id = 12  /* Grab from Alert */
    AND rule.metric_field = 'DURATION_SECONDS'  /* Grab from Alert */
```

This gives you information around how close the `violation_value` was to the threshold and what a new threshold would look like if adjusted to the violation value and its z_score. This gives you an idea of how to adjust the `z_threshold` to mitigate false positives.

### Best Practices

1. **Start Conservative**: Begin with higher threshold multipliers (2.5-3.0) and adjust based on your data patterns
2. **Monitor Multiple Metrics**: Create rules for different metrics to get comprehensive coverage
3. **Regular Review**: Periodically review and adjust rules based on changing data patterns
4. **Sufficient History**: Ensure you have enough historical data for accurate baseline calculations 
5. **Hour-Specific Analysis**: The system analyzes against hour of day, so consider time-of-day patterns

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
uv sync --frozen --compile-bytecode
```
5. Add in pre-commits (you might need to run `source .venv/bin/activate` if your uv environment is not being recognized)
```bash
pre-commit install --install-hooks
```
6. Add in Environment Variables referencing `.env.example`

### Quick Start
```bash
# Start the development server
make dev-compose

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

1. **Start your app**: `make dev-compose`
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

### Load Testing

The Watcher system includes comprehensive load testing capabilities using Locust to simulate realistic pipeline execution patterns and system monitoring.

#### Overview

The load testing suite simulates:
- **1000 pipelines** executing every 5 minutes
- **System monitoring** (freshness, timeliness, Celery queue monitoring)
- **Heartbeat checks** every 5 minutes
- **Realistic data patterns** with random success/failure rates

#### Running Load Tests

```bash
# Start load test (foreground - Ctrl+C to stop)
make load-test

# The test will:
# - Start 1000 users (pipelines) at 10 user/second spawn rate
# - Open web interface at http://localhost:8089
# - Run continuously until stopped
```

#### Load Test Configuration

The load test is configured in `src/diagnostics/locustfile.py` (DO NOT run this on production, it will generate a crap ton of fake data):

- **Pipeline Execution**: Each user simulates one pipeline running every 5 minutes
- **System Checks**: Run every 5 minutes (freshness, timeliness, Celery monitoring)
- **Heartbeat Checks**: Run every 5 minutes to verify system health
- **Realistic Data**: Random processing times (30s-10min), 95% success rate
- **Anomaly Generation**: 1% chance of generating anomalous data to trigger alerts:
  - **High Volume**: 500K-2M total rows (vs normal 1K-100K)
  - **Long Duration**: 30min-2hr processing time (vs normal 30s-10min)
  - **High Activity**: 50K-200K inserts/updates (vs normal 100-10K)

#### Monitoring Load Tests

1. **Locust Web UI**: Access http://localhost:8089 for real-time statistics
2. **Key Metrics**:
   - **RPS**: Requests per second
   - **Response Times**: 50th, 90th, 95th percentiles
   - **Failure Rate**: Percentage of failed requests
   - **Active Users**: Current number of simulated pipelines

3. **Database Monitoring**: Use the diagnostics page at `/diagnostics` to monitor:
   - Connection performance
   - Query execution times
   - Active queries and locks
   - Database health metrics
   - Celery Worker metrics and task performance analytics

#### Load Test Scenarios

The test includes several realistic scenarios:

1. **Pipeline Execution Cycle**:
   - Create/get pipeline
   - Start execution
   - Simulate processing time
   - End execution with results

2. **System Monitoring**:
   - Freshness checks for all pipelines
   - Timeliness validation
   - Celery queue depth monitoring

3. **Error Handling**:
   - Proper failure logging in Locust
   - Detailed error messages for debugging
   - Graceful handling of timeouts

#### Performance Targets

Based on the load test configuration, the system should handle:
- **1000 concurrent pipelines** executing every 5 minutes
- **~3-10 RPS** sustained load (1000 users ÷ 300 seconds)
- **Sub-second response times** for all endpoints
- **<1% failure rate** under normal conditions

#### Troubleshooting Load Tests

**Common Issues**:
1. **High Response Times**: Check database performance and connection pooling
2. **High Failure Rate**: Verify all services are running (FastAPI, PostgreSQL, Redis)
3. **Memory Issues**: Monitor database connection limits and query performance
4. **Celery Timeouts**: Ensure Celery workers are running and Redis is accessible

**Debugging**:
- Check Locust web UI for detailed error messages
- Use `/diagnostics` page to monitor database health
- Review application logs for specific error patterns
- Monitor system resources (CPU, memory, disk I/O)

## 🚀 Deployment

The Watcher system requires several components to run in production. This section outlines the complete deployment architecture and setup requirements.

### Architecture Overview

The Watcher system consists of the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Worker  │    │   PostgreSQL    │
│   (Web API)     │    │ (Background     │    │   (Database)    │
│                 │    │  Tasks)         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │ (Message Queue) │
                    └─────────────────┘
```

### Required Components

#### 1. PostgreSQL Database
- **Purpose**: Primary data storage for all pipeline metadata, execution logs, and anomaly detection results
- **Requirements**: 
  - PostgreSQL 12+ recommended
  - Sufficient storage for historical execution data
  - Regular backups configured
- **Configuration**: Set `PROD_DATABASE_URL` environment variable

#### 2. Redis Instance
- **Purpose**: Message broker for Celery background tasks
- **Requirements**:
  - Redis 6+ recommended
  - Persistent storage enabled
  - Memory allocation based on expected task volume
- **Configuration**: Set `PROD_REDIS_URL` environment variable

#### 3. FastAPI Application Container
- **Purpose**: Main web API for pipeline execution tracking and monitoring
- **Features**:
  - REST API endpoints
  - Database connections
  - Slack webhook integration
  - Health checks and monitoring
- **Configuration**: Set `PROD_SLACK_WEBHOOK_URL` and other production environment variables

#### 4. Celery Worker Container
- **Purpose**: Background task processing for non-critical tasks
- **Features**:
  - Anomaly detection processing
  - Log cleanup tasks
  - Timeliness & Freshness checks
  - Slack alert notifications
- **Configuration**: Set `PROD_SLACK_WEBHOOK_URL` environment variable
- **Scaling**: Can run multiple worker instances for high throughput

#### 5. Logfire Account Setup
- **Purpose**: Application monitoring and observability
- **Setup Required**:
  1. Create account at [logfire.pydantic.dev](https://logfire.pydantic.dev)
  2. Generate API token (Free Account gives you 10 million calls per month!)
  3. Configure `PROD_LOGFIRE_TOKEN` environment variable for both FastAPI and Celery containers
- **Benefits**:
  - Request tracing
  - Performance monitoring & Alerting
  - Error & Celery Task tracking
  - Database query analysis

### Environment Variables

FASTAPI Example
```bash
# Database Configuration
PROD_DATABASE_URL=postgresql://user:password@postgres-host:5432/watcher_prod

# Redis Configuration
PROD_REDIS_URL=redis://redis-host:6379/1

# Slack Integration
PROD_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Logfire Monitoring
PROD_LOGFIRE_TOKEN=your-logfire-token-here
PROD_LOGFIRE_CONSOLE=false

# Feature Flags
PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true
PROD_PROFILING_ENABLED=false
```

Celery Example
```bash
# Database Configuration
PROD_DATABASE_URL=postgresql://user:password@postgres-host:5432/watcher_prod

# Redis Configuration
PROD_REDIS_URL=redis://redis-host:6379/1

# Slack Integration
PROD_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Logfire Monitoring
PROD_LOGFIRE_TOKEN=your-logfire-token-here
PROD_LOGFIRE_CONSOLE=false
```

### Database Migration
Before starting the application, run the database migrations on the Prod database:  
(You can always implement the `start.sh` script into the DockerFile as well, it is only used in the dev-compose right now...)
```bash
# With PROD_DATABASE_URL set
make trigger-migration
```

### Production Considerations

#### Security
- Use strong, unique passwords for database and Redis
- Enable SSL/TLS for database connections
- Restrict network access to database and Redis
- Use secrets management for sensitive environment variables
   - I would recommend using a secret manager. Setup new environment variables with the name of the secrets and create a module that pulls the secrets and then assigns them to the appropriate variables in `settings.py`


#### Monitoring
- Set up health checks for all services
    - Create scheduled jobs that ping the `freshness`, `timeliness`, and `log_cleanup`, and `celery/monitor-queue` endpoints on a desired cadence
- Monitor database connection pools
- Track Celery task queue depth

#### Scaling
- **Horizontal Scaling**: Add more Celery worker instances
- **Database Scaling**: Consider read replicas for reporting queries
- **Redis Scaling**: Use Redis Cluster for high availability

#### Backup Strategy
- **Database Backups**: Daily automated backups with point-in-time recovery
- **Redis Persistence**: Enable AOF and RDB persistence
- **Configuration Backup**: Version control all environment configurations

### Health Checks

The application provides several health check endpoints:

- `GET /` - Basic heartbeat
- Database connectivity checks through the webpage `/diagnostics`
- Celery worker and queue monitoring through the webpage `/diagnostics`

### Troubleshooting

#### Common Issues
1. **Database Connection Errors**: Verify `PROD_DATABASE_URL` format and network connectivity
2. **Celery Task Failures**: Check Redis connectivity and worker logs
3. **Slack Notifications Not Working**: Verify webhook URL and permissions
4. **Logfire Not Receiving Data**: Check token validity and network access
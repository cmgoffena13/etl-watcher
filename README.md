# Watcher
**Open Source Metadata Framework for Data Pipeline Monitoring & Lineage Tracking**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, store watermarks, track data lineage, ensure timeliness, detect anomalies, and manage data addresses across your data infrastructure.

![linesofcode](https://aschey.tech/tokei/github/cmgoffena13/watcher?category=code)

## Table of Contents

1. [Development Setup](#development-setup)
2. [Configuration](#configuration)
3. [Features](#features)
4. [API Endpoints](#-api-endpoints)
5. [Documentation](#-documentation)
6. [Database Schema](#️-database-schema)
7. [Development](#️-development)
8. [Technology Stack](#️-technology-stack)
9. [Timeliness & Freshness](#-timeliness--freshness)
10. [Anomaly Checks](#-anomaly-checks)
11. [Log Cleanup](#-log-cleanup--maintenance)
12. [Complete Pipeline Workflow Example](#complete-pipeline-workflow-example)

## Development Setup
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

## Configuration

Watcher supports various configuration options through environment variables. The system uses different prefixes for different environments:

- **Development**: `DEV_` prefix
- **Production**: `PROD_` prefix  
- **Testing**: `TEST_` prefix

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `None` | Yes |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | `None` | No |
| `LOGFIRE_TOKEN` | Logfire token for logging | `None` | No |
| `LOGFIRE_CONSOLE` | Enable console logging | `None` | No |
| `WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES` | Auto-create anomaly detection rules for new pipelines | `False` | No |

### Auto-Create Anomaly Detection Rules

When `WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES` is set to `true`, the system automatically creates anomaly detection rules for all available metrics when a new pipeline is created. This includes rules for:

- **Duration Monitoring**: `duration_seconds` - Tracks pipeline execution time
- **DML Operations**: `inserts`, `updates`, `soft_deletes` - Monitors data modification counts
- **Volume Monitoring**: `total_rows` - Tracks total rows processed

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

**Note**: When auto-creation is enabled, default anomaly detection rules are created with standard thresholds. You may want to customize these rules after creation based on your specific pipeline patterns and requirements.

## Features

### 🔄 Pipeline Execution Monitoring
- **Execution Tracking**: Start and end pipeline executions with detailed metadata to track performance
- **Performance Metrics**: Track duration, DML counts (inserts, updates, deletes), and total rows processed
- **Execution History**: Maintain complete audit trail of all pipeline runs
- **Status Management**: Monitor active/inactive pipeline states

### ⏰ Timeliness & Freshness Checks
- **Pipeline Execution Timeliness**: Monitor if pipeline executions complete within expected timeframes
- **DML Freshness Monitoring**: Check if data manipulation operations (inserts, updates, deletes) are recent enough
- **Configurable Thresholds**: Set custom rules per pipeline type and individual pipelines
- **Mute Capability**: Skip checks for specific pipelines when needed

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
- **Configurable Metrics**: Monitor duration, row counts, and DML operations
- **Pipeline-Specific Rules**: Create custom anomaly detection rules per pipeline
- **Automatic Detection**: Run anomaly detection automatically after pipeline execution
- **Confidence Scoring**: Calculate confidence scores based on statistical deviation
- **Lookback Periods**: Analyze historical data over configurable time windows

### 🧹 Log Cleanup
- **Automated Maintenance**: Remove old log data to maintain database performance
- **Batch Processing**: Safe deletion in configurable batches to avoid database locks
- **Cascading Cleanup**: Maintains referential integrity across related tables
- **Configurable Retention**: Set custom retention periods for different data types

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

### Monitoring & Health
- `POST /timeliness` - Check pipeline execution timeliness (requires `lookback_minutes` parameter)
- `POST /freshness` - Check DML operation freshness
- `POST /log_cleanup` - Clean up old log data
- `GET /` - Health check endpoint
- `GET /scalar` - Interactive API documentation

## 📖 Documentation
The repo utilizes Scalar for interactive API documentation found at the `/scalar` route. This provides an intuitive interface to explore and test all available endpoints.

## 🗄️ Database Schema

### Core Tables
- **`pipeline`** - Pipeline definitions with configuration and metadata
- **`pipeline_type`** - Pipeline type definitions and broad timeliness rules
- **`pipeline_execution`** - Individual pipeline execution records and metrics
- **`address`** - Data address definitions (databases, files, APIs, etc.)
- **`address_type`** - Address type categorization
- **`address_lineage`** - Source-to-target data lineage relationships
- **`address_lineage_closure`** - Optimized closure table for efficient lineage queries
- **`timeliness_pipeline_execution_log`** - Log of pipeline executions exceeding timeliness thresholds
- **`freshness_pipeline_log`** - Log of pipelines failing freshness checks
- **`anomaly_detection_rule`** - Anomaly detection rules and configuration per pipeline
- **`anomaly_detection_result`** - Detected anomalies with statistical analysis and confidence scores

### Database Key Features
- **PostgreSQL JSONB** for flexible configuration storage
- **Timezone-aware timestamps** for all datetime fields
- **Optimized indexes** for performance-critical queries
- **Foreign key constraints** for data integrity
- **Closure table pattern** for efficient lineage traversal

## 🛠️ Development

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

### Development Workflow
1. **Adding New Tables**: Add model to `src.database.models.__init__.py` for SQLModel metadata
2. **Database Migrations**: Use `make add-migration` to generate migration scripts
3. **Testing**: Use `make test` to run the comprehensive test suite
4. **Code Quality**: Pre-commit hooks automatically format and lint code

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and settings management using Python type annotations
- **SQLModel** - SQL databases in Python, designed for simplicity and compatibility
- **PostgreSQL** - Robust relational database with JSONB support
- **Alembic** - Database migration tool for SQLAlchemy
- **AsyncPG** - Async PostgreSQL driver
- **HTTPX** - Async HTTP client for external API calls (Slack)

### Development & Testing
- **Pytest** - Testing framework with async support
- **Ruff** - Fast Python linter and formatter
- **Pre-commit** - Git hooks for code quality
- **UV** - Fast Python package manager

### Monitoring & Observability
- **Logfire** - Structured logging and observability
- **Rich** - Rich text and beautiful formatting in the terminal
- **Scalar** - Interactive API documentation

### Infrastructure
- **Docker** - Containerization
- **Uvicorn** - ASGI server for FastAPI
- **Pendulum** - Better dates and times for Python

## ⏰ Timeliness & Freshness

The monitoring system provides two complementary checks to ensure your data pipelines are running optimally:

### Pipeline Execution Timeliness
Monitors if pipeline executions complete within expected timeframes, helping identify performance issues and long-running processes. Uses a configurable lookback window to check both running and completed pipelines to alert on long-running pipelines as well.

### DML Freshness Monitoring  
Checks if data manipulation operations (inserts, updates, deletes) are recent enough, ensuring data freshness for downstream consumers.

### How It Works

The timeliness check runs on a configurable schedule through the two endpoints: `freshness` and `timeliness` (ping the endpoint as often as you like, it does broad coverage) and evaluates each pipeline against its defined rules.

#### Timeliness Check Features
- **Lookback Window**: Configurable time window to check for overdue executions (e.g., last 60 minutes)
- **Running Pipeline Detection**: Identifies currently running pipelines that exceed their threshold
- **Completed Pipeline Detection**: Identifies completed pipelines that took longer than expected
- **Dynamic Thresholds**: Uses pipeline-specific or pipeline-type-specific timeliness settings

### Configuration

Timeliness rules can be set at two levels:

#### Pipeline Type Level (Parent Rules)
Set broad timeliness rules that apply to all pipelines of a specific type:

```python
pipeline_type_data = {
    "name": "api-integration",
    "group_name": "extraction", 
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

The timeliness system supports granular time windows for flexible monitoring configurations. You can set any combination of time unit and number to create precise timeliness rules:

- **MINUTE** - Check every N minutes (e.g., 5 minutes, 30 minutes)
- **HOUR** - Check every N hours (e.g., 1 hour, 6 hours, 12 hours)  
- **DAY** - Check every N days (e.g., 1 day, 3 days, 7 days)
- **WEEK** - Check every N weeks (e.g., 1 week, 2 weeks, 4 weeks)
- **MONTH** - Check every N months (e.g., 1 month, 3 months, 6 months)
- **YEAR** - Check every N years (e.g., 1 year, 2 years)

### Priority System

1. **Child Rules** - Pipeline-specific settings take precedence
2. **Parent Rules** - Fall back to pipeline type settings
3. **Skip** - If neither child nor parent rules are configured, the pipeline is skipped

### DML Tracking

The system tracks the most recent DML operation across three types:
- **INSERT** operations (`last_target_insert`)
- **UPDATE** operations (`last_target_update`) 
- **SOFT DELETE** operations (`last_target_soft_delete`)

The timeliness check uses the **most recent** of these three timestamps as the baseline for comparison. These fields are calculated behind the scenes from the DML operations data provided when ending a pipeline execution.

### Mute Capability

Pipelines can be temporarily excluded from timeliness checks:

```python
# Mute freshness checks for a specific pipeline
pipeline_data = {
    "name": "maintenance-pipeline",
    "mute_freshness_check": True
}

# Mute timeliness checks for a specific pipeline
pipeline_data = {
    "name": "long-running-pipeline",
    "mute_timeliness_check": True
}

# Mute both checks for an entire pipeline type
pipeline_type_data = {
    "name": "batch-processing",
    "mute_freshness_check": True,
    "mute_timeliness_check": True
}
```

### Execution Logging

Long-running pipeline executions are automatically logged to the `timeliness_pipeline_execution_log` table when they exceed the configured threshold (default: 30 minutes).

### Slack Notifications

The timeliness system sends Slack notifications for two types of issues:

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
• Total Overdue: 2
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
• Total Overdue: 2
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

if result["status"] == "warning":
    print("Timeliness check completed with warnings - some executions are overdue")
    print("Check Slack notifications for detailed information")
elif result["status"] == "success":
    print("All pipeline executions are running on time")
else:
    print(f"Unexpected status: {result['status']}")
```

#### DML Freshness Monitoring
```python
# Check DML operation freshness
response = await client.post("http://localhost:8000/freshness")
result = response.json()

if result["status"] == "warning":
    print("Freshness check completed with warnings - some DML operations are stale")
    print("Check Slack notifications for detailed information")
elif result["status"] == "success":
    print("All DML operations are fresh")
else:
    print(f"Unexpected status: {result['status']}")
```

#### Response Status Codes

- **200 OK**: Timeliness check completed successfully
  - `{"status": "success"}` - All pipelines are running on time
  - `{"status": "warning"}` - Some pipelines are overdue (Slack notifications sent)

#### Input Parameters

- **`lookback_minutes`** (required): Time window in minutes to check for overdue executions
  - Example: `60` - Check executions from the last 60 minutes
  - Example: `1440` - Check executions from the last 24 hours
  - Example: `10080` - Check executions from the last week

### Error Handling

The timeliness system provides comprehensive error handling and monitoring:

#### Slack Notifications
When timeliness issues are detected, detailed Slack notifications are automatically sent with:
- **Pipeline Information**: Pipeline ID, name, and overdue duration
- **DML Timestamps**: Last insert, update, and soft delete timestamps  
- **Expected Timeframe**: Configured timeliness rules and thresholds
- **Specific Details**: Exact duration beyond expected timeframe

#### Graceful Degradation
- **Non-Blocking**: Timeliness failures don't interrupt the check process
- **Comprehensive Logging**: All issues are logged for debugging and analysis
- **Status Reporting**: API returns warning status for programmatic handling
- **Notification Reliability**: Failed Slack notifications are logged but don't affect timeliness detection

#### Monitoring Integration
- **Real-time Alerts**: Immediate Slack notifications for urgent issues
- **Historical Tracking**: All timeliness issues are logged to the database
- **Watermark Filtering**: Notifications only alert on new executions within the current watermark range
- **Pipeline Context**: Clear identification of which specific pipeline had issues

This comprehensive error handling ensures you're immediately notified of data freshness issues while maintaining system reliability and providing detailed context for quick resolution.

## 🚨 Anomaly Checks

The anomaly detection system provides statistical analysis to identify unusual patterns in pipeline execution metrics, helping you quickly spot performance issues and data quality problems.

### How It Works

Anomaly detection uses statistical methods to analyze historical pipeline execution data and identify outliers:

1. **Baseline Calculation**: Analyzes historical execution data over a configurable lookback period
2. **Statistical Analysis**: Uses standard deviation and z-score calculations to determine normal ranges
3. **Threshold Detection**: Flags executions that exceed configurable statistical thresholds
4. **Confidence Scoring**: Provides confidence scores based on how far outside normal ranges the execution falls

### Configuration

#### Rule Creation
Create anomaly detection rules per pipeline with the following parameters:

- **`pipeline_id`**: Target pipeline to monitor
- **`name`**: Descriptive name for the rule
- **`metric_field`**: Metric to monitor (duration_seconds, total_rows, total_inserts, etc.)
- **`lookback_days`**: Number of days of historical data to analyze (default: 7)
- **`minimum_executions`**: Minimum executions needed for baseline calculation (default: 5)
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

Anomaly detection runs automatically after each pipeline execution:

1. **Trigger**: Executes when `end_pipeline_execution` is called
2. **Rule Lookup**: Finds active rules for the completed pipeline
3. **Historical Analysis**: Analyzes execution history for the same hour of day
4. **Statistical Calculation**: Computes baseline mean and standard deviation
5. **Anomaly Detection**: Identifies executions exceeding thresholds
6. **Notification**: Sends Slack alerts for detected anomalies

### Slack Notifications

When anomalies are detected, the system sends detailed Slack notifications including:

- **Rule Information**: Rule name, metric being monitored, threshold settings
- **Anomaly Details**: Execution ID, actual value, baseline value, deviation percentage
- **Confidence Score**: Statistical confidence in the anomaly detection
- **Context**: Lookback period, execution count, z-score

Example notification:
```
⚠️ WARNING
Timestamp: 2025-01-09 20:30:45 UTC
Message: Anomaly detected in pipeline 123 - 2 execution(s) flagged

Details:
• Rule: Duration Anomaly Detection
• Metric: duration_seconds
• Threshold Multiplier: 2.0
• Lookback Days: 7
• Anomalies:
  • Execution ID 456: 3600 (baseline: 1200.00, deviation: 200.0%, confidence: 0.85)
  • Execution ID 457: 4200 (baseline: 1200.00, deviation: 250.0%, confidence: 0.92)
```

### Best Practices

1. **Start Conservative**: Begin with higher threshold multipliers (2.5-3.0) and adjust based on your data patterns
2. **Monitor Multiple Metrics**: Create rules for different metrics to get comprehensive coverage
3. **Regular Review**: Periodically review and adjust rules based on changing data patterns
4. **Sufficient History**: Ensure you have enough historical data for accurate baseline calculations
5. **Hour-Specific Analysis**: The system analyzes data by hour of day, so consider time-of-day patterns

### Error Handling

The anomaly detection system includes robust error handling:

- **Insufficient Data**: Rules are skipped if not enough historical executions exist
- **Missing Metrics**: Executions with null metric values are excluded from analysis
- **Database Errors**: Failed detections are logged but don't interrupt pipeline execution
- **Notification Failures**: Slack notification failures are logged but don't affect anomaly detection

This comprehensive anomaly detection system helps maintain data quality and performance by automatically identifying unusual patterns in your pipeline executions.

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

The system cleans up data from three main log tables:

#### 1. Pipeline Executions
- **Table**: `pipeline_execution`
- **Filter**: Records with `start_date <= retention_date`
- **Purpose**: Removes old pipeline execution records

#### 2. Timeliness Logs
- **Table**: `timeliness_pipeline_execution_log`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old timeliness check logs

#### 3. Anomaly Detection Results
- **Table**: `anomaly_detection_result`
- **Filter**: Records with `pipeline_execution_id <= max_pipeline_execution_id`
- **Purpose**: Removes old anomaly detection results

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
        

if __name__ == "__main__":
    asyncio.run(run_pipeline_workflow())
```
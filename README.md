# Watcher
**Open Source Metadata Framework for Data Pipeline Monitoring & Lineage Tracking**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, track data lineage, ensure timeliness, detect anomalies, and manage data addresses across your data infrastructure.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Features](#features)
3. [API Endpoints](#-api-endpoints)
4. [Documentation](#-documentation)
5. [Database Schema](#-database-schema)
6. [Development](#️-development)
7. [Technology Stack](#️-technology-stack)
8. [Timeliness](#-timeliness)
9. [Complete Pipeline Workflow Example](#complete-pipeline-workflow-example)

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

## Features

### 🔄 Pipeline Execution Monitoring
- **Execution Tracking**: Start and end pipeline executions with detailed metadata to track performance
- **Performance Metrics**: Track duration, DML counts (inserts, updates, deletes), and total rows processed
- **Execution History**: Maintain complete audit trail of all pipeline runs
- **Status Management**: Monitor active/inactive pipeline states

### ⏰ Timeliness Checks
- **Automated Monitoring**: Check if pipelines are running within expected timeframes
- **Configurable Thresholds**: Set custom timeliness rules per pipeline type and individual pipelines
- **Mute Capability**: Skip timeliness checks for specific pipelines when needed

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
- **Configurable Metrics**: Monitor duration, row counts, DML operations, and processing rates
- **Pipeline-Specific Rules**: Create custom anomaly detection rules per pipeline
- **Automatic Detection**: Run anomaly detection automatically after pipeline execution
- **Confidence Scoring**: Calculate confidence scores based on statistical deviation
- **Lookback Periods**: Analyze historical data over configurable time windows

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
- `POST /timeliness` - Check pipeline timeliness
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

## ⏰ Timeliness

The timeliness system provides automated monitoring to ensure your data pipelines are running within expected timeframes. This helps maintain data freshness and catch issues before they impact downstream consumers.

### How It Works

The timeliness check runs on a configurable schedule (ping the endpoint as often as you like, it does broad coverage) and evaluates each pipeline against its defined timeliness rules. It examines the last DML (Data Manipulation Language) operation timestamp and compares it against the expected timeframe.

### Configuration

Timeliness rules can be set at two levels:

#### Pipeline Type Level (Parent Rules)
Set broad timeliness rules that apply to all pipelines of a specific type:

```python
pipeline_type_data = {
    "name": "api-integration",
    "group_name": "extraction", 
    "timely_number": 12,
    "timely_datepart": "hour",
    "mute_timely_check": False
}
```

#### Pipeline Level (Child Rules)
Override parent rules with pipeline-specific settings:

```python
pipeline_data = {
    "name": "critical-data-pipeline",
    "timely_number": 2,
    "timely_datepart": "hour",
    "mute_timely_check": False
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
# Mute a specific pipeline
pipeline_data = {
    "name": "maintenance-pipeline",
    "mute_timely_check": True
}

# Mute an entire pipeline type
pipeline_type_data = {
    "name": "batch-processing",
    "mute_timely_check": True
}
```

### Execution Logging

Long-running pipeline executions are automatically logged to the `timeliness_pipeline_execution_log` table when they exceed the configured threshold (default: 30 minutes).

### API Usage

```python
# Check timeliness for all pipelines
response = await client.post("http://localhost:8000/timeliness")
if response.status_code == 500:
    print("Timeliness check failed - some pipelines are overdue")
    print(response.json()["detail"])
else:
    print("All pipelines are running on time")
```

### Error Handling

When pipelines fail timeliness checks, the system returns detailed error messages including:
- Pipeline ID and name
- Last DML operation timestamp
- Expected timeframe
- Specific overdue duration

This information helps quickly identify and resolve data freshness issues.

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
        start_time = pendulum.now("UTC")
        execution_start_data = {
            "pipeline_id": pipeline_result['id'],
            "start_date": start_time.isoformat()
        }
        
        start_response = await client.post("http://localhost:8000/start_pipeline_execution", json=execution_start_data)
        execution_start = start_response.json()
        execution_id = execution_start['id']
        
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
        end_time = pendulum.now("UTC")
        execution_end_data = {
            "id": execution_id,
            "end_date": end_time.isoformat(),
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
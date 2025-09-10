# Watcher
**Open Source Metadata Framework for Data Pipeline Monitoring & Lineage Tracking**

A comprehensive FastAPI-based metadata management system designed to monitor data pipeline executions, track data lineage, ensure timeliness, and manage data addresses across your data infrastructure.

## Table of Contents

1. [Setup](##Setup)
2. [Features](##Features)
3. [API Endpoints](##API-Endpoints)
4. [Documentation](##Documentation)
5. [Database Schema](##Database-Schema)
6. [Development](##Development)
7. [Technology Stack](##Technology-Stack)
8. [Complete Pipeline Workflow Example](#complete-pipeline-workflow-example)

## Setup
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

### Monitoring & Health
- `POST /timeliness` - Check pipeline timeliness
- `GET /` - Health check endpoint
- `GET /scalar` - Interactive API documentation

## 📖 Documentation
The repo utilizes Scalar for interactive API documentation found at the `/scalar` route. This provides an intuitive interface to explore and test all available endpoints.

## 🗄️ Database Schema

### Core Tables
- **`pipeline`** - Pipeline definitions with configuration and metadata
- **`pipeline_type`** - Pipeline type definitions and timeliness rules
- **`pipeline_execution`** - Individual pipeline execution records and metrics
- **`address`** - Data address definitions (databases, files, APIs, etc.)
- **`address_type`** - Address type categorization
- **`address_lineage`** - Source-to-target data lineage relationships
- **`address_lineage_closure`** - Optimized closure table for efficient lineage queries
- **`timeliness_pipeline_execution_log`** - Log of pipeline executions exceeding timeliness thresholds

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

## Complete Pipeline Workflow Example
```python
import httpx
import asyncio
import pendulum

async def run_pipeline_workflow():
    """Complete example of creating and running a pipeline with lineage tracking"""

    # This would be: SELECT MAX(id) FROM your_table or whatever you're working with
    max_id_from_source = 150

    # Step 1: Create Pipeline Record
    # If Pipeline exists, an id is returned anyway
    pipeline_data = {
        "name": "stock-price-worker",
        "pipeline_type_name": "api-integration",
        "pipeline_type_group_name": "extraction",
        "load_lineage": True
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
        if pipeline_result['load_lineage']:
            lineage_data = {
                "pipeline_id": pipeline_result['id'],
                "source_addresses": [
                    {
                        "address_name": "api.stockdata.com/v1/prices",
                        "address_type_name": "api",
                        "address_type_group_name": "external"
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
        SELECT
        *
        FROM Table_A
        WHERE id > watermark
            AND id <= next_watermark
        
        # Step 6: End Pipeline Execution (with DML counts gathered from work)
        end_time = pendulum.now("UTC")
        execution_end_data = {
            "id": execution_id,
            "end_date": end_time.isoformat(),
            "inserts": 150,
            "updates": 25,
            "soft_deletes": 5,
            "total_rows": 180
        }
        
        # Ending execution automatically increments watermark to next_watermark
        await client.post("http://localhost:8000/end_pipeline_execution", json=execution_end_data)
        print("Pipeline execution completed successfully")
        

if __name__ == "__main__":
    asyncio.run(run_pipeline_workflow())
```
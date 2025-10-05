Welcome to Watcher's documentation!
=====================================

Watcher is a comprehensive data pipeline monitoring and anomaly detection system designed to ensure your data pipelines are running optimally and detect issues before they impact your business.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/installation
   getting_started/quick_start
   getting_started/configuration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/endpoints
   api/models
   api/celery_tasks

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/pipeline_management
   guides/anomaly_detection
   guides/monitoring
   guides/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/database_schema
   reference/migrations
   reference/deployment

Key Features
============

- **Pipeline Monitoring** - Track execution timing and data freshness
- **Anomaly Detection** - Statistical analysis of pipeline patterns  
- **Data Lineage** - Track relationships between data sources
- **Health Checks** - Comprehensive system monitoring
- **Background Processing** - Celery-based distributed task processing

Quick Start
===========

.. code-block:: bash

   # Installation
   uv sync
   docker-compose up -d

   # Run migrations
   alembic upgrade head

   # Start the application
   uv run python src/app.py

The application will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/scalar`.
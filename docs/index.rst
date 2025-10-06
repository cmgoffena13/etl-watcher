Welcome to Watcher's documentation!
=====================================

.. image:: _static/images/watcher.jpg
   :alt: Watcher Logo
   :align: center
   :width: 200px

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

   api/celery_tasks
   api/endpoints
   api/models

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/address_lineage
   guides/anomaly_detection
   guides/custom_querying
   guides/log_cleanup
   guides/monitoring
   guides/pipeline_management
   guides/polygon_example
   guides/watermark_management

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/architecture
   reference/database_schema
   reference/migrations

Key Features
============

- **Pipeline Monitoring** - Track execution timing and data freshness
- **Anomaly Detection** - Statistical analysis of pipeline patterns  
- **Address Lineage** - Track relationships between data sources
- **Health Checks** - Comprehensive system monitoring
- **Background Processing** - Celery-based distributed task processing

Quick Start
===========

.. code-block:: bash

   # Installation
   uv sync
   docker-compose up -d

The application will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/scalar`.
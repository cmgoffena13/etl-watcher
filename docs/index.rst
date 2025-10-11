Welcome to Watcher's documentation!
=====================================

.. image:: _static/images/watcher.jpg
   :alt: Watcher Logo
   :align: center
   :width: 100%
   :class: logo-responsive

Watcher is a comprehensive data pipeline monitoring and anomaly detection system designed to 
ensure your data pipelines are running optimally and detect issues before they impact your business.


Key Features
============

- **Execution Tracking** - Start and end pipeline executions with detailed metadata to track performance
- **Pipeline Monitoring** - Track execution timing and data freshness
- **Anomaly Detection** - Statistical analysis of pipeline patterns  
- **Address Lineage** - Track relationships between data sources
- **Background Processing** - Celery-based distributed task processing
- **Source Control Integration** - Pipeline configuration and lineage stored in version control


Source Control Integration
===========================

Watcher is designed to work seamlessly with source control systems. Your pipeline configuration and address lineage definitions should be stored alongside your ETL code in version control:

**Pipeline Configuration:**

- Store pipeline definitions in the same repository as your ETL code
- Use environment variables for dynamic values (API keys, database URLs)
- Track changes to pipeline configuration over time
- Review pipeline changes alongside code changes

**Address Lineage:**

- Define lineage relationships in your pipeline code
- Version control lineage changes with your data transformations
- Ensure lineage stays synchronized with your actual data flow
- Document data dependencies in your codebase

**Benefits:**

- **Reproducibility**: Same configuration across all environments
- **Collaboration**: Team members can see and modify pipeline definitions
- **Documentation**: Pipeline purpose and lineage documented in code
- **Rollback**: Easy to revert problematic pipeline changes
- **Code Review**: Review pipeline changes alongside code changes

Quick Start
===========

.. code-block:: bash

   docker-compose up -d

- The application will be available at `http://localhost:8000`
- Interactive API documentation will be available at `http://localhost:8000/scalar`

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

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/address_lineage
   guides/anomaly_detection
   guides/custom_querying
   guides/etl_example
   guides/log_cleanup
   guides/monitoring
   guides/pipeline_management
   guides/recommended_implementation
   guides/watermark_management

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/architecture
   reference/celery_tasks
   reference/database_schema
   reference/dev_kubernetes

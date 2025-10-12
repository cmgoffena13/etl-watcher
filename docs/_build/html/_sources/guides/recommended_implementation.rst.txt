Recommended Implementation - SDK
================================

This guide covers the recommended implementation using the ``etl-watcher-sdk`` Python SDK to integrate your ETL code with Watcher.

.. note::
    The ``etl-watcher-sdk`` simplifies the integration process by providing a clean Python API.
    See the docs here: https://etl-watcher-sdk.readthedocs.io/en/latest/

Installation
~~~~~~~~~~~~

Install the SDK using your preferred package manager:

.. tabs::

   .. tab:: uv

      .. code-block:: bash

         uv add etl-watcher-sdk

   .. tab:: pip

      .. code-block:: bash

         pip install etl-watcher-sdk

   .. tab:: poetry

      .. code-block:: bash

         poetry add etl-watcher-sdk

Key Processes
~~~~~~~~~~~~~~

1. Define Pipeline Configuration
2. Initialize Watcher Client
3. Sync Pipeline Configuration
4. Track Pipeline Execution

Define Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store your pipeline configuration in source control using the SDK's data models:

.. code-block:: python

    import pendulum
    from watcher import Address, AddressLineage, Pipeline, PipelineConfig

    POLYGON_OPEN_CLOSE_PIPELINE_CONFIG = PipelineConfig(
        pipeline=Pipeline(
            name="polygon_open_close",
            pipeline_type_name="extraction",
            timeliness_number=20,
            timeliness_datepart="minute",
            freshness_number=1,
            freshness_datepart="day",
            pipeline_metadata={
                "description": "Daily stock price extraction from Polygon API",
                "owner": "data-team",
            },
        ),
        address_lineage=AddressLineage(
            source_addresses=[
                Address(
                    name="https://api.polygon.io/v1/open-close/",
                    address_type_name="polygon",
                    address_type_group_name="api",
                )
            ],
            target_addresses=[
                Address(
                    name="prod.polygon.open_close",
                    address_type_name="postgres",
                    address_type_group_name="database",
                )
            ],
        ),
        default_watermark=pendulum.date(2025, 10, 1).to_date_string(),
        next_watermark=pendulum.now().date().to_date_string(),
    )

Initialize Watcher Client
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a Watcher client instance:

.. code-block:: python

    from watcher import Watcher

    # Initialize the Watcher client
    watcher = Watcher("http://localhost:8000")

Sync Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the SDK to sync your pipeline configuration and address lineage with Watcher:

.. code-block:: python

    # Sync pipeline configuration with Watcher
    synced_config = watcher.sync_pipeline_config(POLYGON_OPEN_CLOSE_PIPELINE_CONFIG)

.. note::
    The synchronization also handles watermark management!

Track Pipeline Execution
~~~~~~~~~~~~~~~~~~~~~~~~

Use the SDK's decorator to track your ETL pipeline execution:

.. code-block:: python

    from watcher import ETLResult, WatcherContext

    @watcher.track_pipeline_execution(
        pipeline_id=synced_config.pipeline.id,
        active=synced_config.pipeline.active,
        watermark=synced_config.watermark,
        next_watermark=synced_config.next_watermark,
    )
    def extract_data(watcher_context: WatcherContext, tickers: list[str]):
        # Access watermark and next_watermark from the context
        watermark = pendulum.parse(watcher_context.watermark).date()
        next_watermark = pendulum.parse(watcher_context.next_watermark).date()
        
        # Your ETL logic here
        total_rows = 0
        for ticker in tickers:
            # Process each ticker...
            total_rows += process_ticker(ticker, watermark, next_watermark)
        
        # Return ETL results
        return ETLResult(
            completed_successfully=True,
            total_rows=total_rows,
        )

The decorator automatically handles:

- Starting and ending pipeline execution
- Updating the pipeline execution with the ETLResult
- Active/Inactive pipeline management
- All HTTP communication with the Watcher API

And provides access to the ``watcher_context``, allowing for:

- Access to the watermark and next_watermark
- Access to the pipeline execution context (for hiearchical execution tracking)

Complete Example
~~~~~~~~~~~~~~~~

Here's a complete example putting it all together:

.. code-block:: python

    import time
    import httpx
    import pendulum
    from watcher import ETLResult, Watcher, WatcherContext
    from pipeline import POLYGON_OPEN_CLOSE_PIPELINE_CONFIG

    # Initialize Watcher client
    watcher = Watcher("http://localhost:8000")

    # Sync pipeline configuration
    synced_config = watcher.sync_pipeline_config(POLYGON_OPEN_CLOSE_PIPELINE_CONFIG)

    # Define your ETL function with tracking
    @watcher.track_pipeline_execution(
        pipeline_id=synced_config.pipeline.id,
        active=synced_config.pipeline.active,
        watermark=synced_config.watermark,
        next_watermark=synced_config.next_watermark,
    )
    def extract_data(watcher_context: WatcherContext, tickers: list[str]):
        # Access the watcher_context to get the watermark and next_watermark
        watermark = pendulum.parse(watcher_context.watermark).date()
        next_watermark = pendulum.parse(watcher_context.next_watermark).date()
        
        all_records = []
        total_rows = 0
        
        for ticker in tickers:
            date = watermark
            while date < next_watermark:
                response = httpx.get(
                    f"https://api.polygon.io/v1/open-close/{ticker}/{date}",
                    params={"apiKey": "YOUR_API_KEY"},
                )
                
                if response.status_code == 429:
                    time.sleep(30)  # Rate limit handling
                    continue
                
                record = response.json()
                if record["status"] == "OK":
                    all_records.append(record)
                
                date = date.add(days=1)
            
            total_rows += len(all_records)
        
        # Make sure to return the ETLResult
        return ETLResult(
            completed_successfully=True,
            total_rows=total_rows,
        )

    # Execute your ETL pipeline
    tickers = ["AAPL", "META"]
    extract_data(tickers=tickers)

Benefits of Using the SDK
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Simplified Integration**: Abstracts away complex HTTP requests and API interactions
- **Synchronization**: Automatically syncs pipeline configuration and address lineage with Watcher
- **Watermark Management**: Automatically manages watermarks for each pipeline execution
- **Execution Tracking**: Automatically tracks pipeline execution and updates the pipeline execution with the ETLResult
- **Hierarchical Execution Tracking**: Provides access to the ``watcher_context`` for hierarchical execution tracking

This implementation provides a clean, maintainable way to integrate your ETL processes with 
the Watcher framework.
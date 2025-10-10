Recommended Implementation
============================

This guide covers the recommended implementation to have your code integrated with Watcher.

.. note::
    Currently developing out an `SDK <https://github.com/cmgoffena13/etl-watcher-sdk>`_ to simplify the implementation. 
    See the docs here: https://etl-watcher-sdk.readthedocs.io/en/latest/

Key Processes
~~~~~~~~~~~~~~

1. Sync Pipeline Configuration
    a. Handle Watermark Management
2. Sync Address Lineage
3. Handle Pipeline Execution

Sync Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store your pipeline configuration in source control. Example:

.. code-block:: python

        PIPELINE_CONFIG = {
            "pipeline": {
                "name": "polygon_open_close",
                "pipeline_type_name": "extraction",
                "timeliness_number": 20,
                "timeliness_datepart": "minute",
                "freshness_number": 1,
                "freshness_datepart": "day",
                "pipeline_metadata": {
                    "description": "Daily stock price extraction from Polygon API",
                    "owner": "data-team",
                },
            },
            "lineage": {
                "pipeline_id": None,  # Will be set later
                "source_addresses": [
                    {
                        "name": "https://api.polygon.io/v1/open-close/",
                        "address_type_name": "polygon",
                        "address_type_group_name": "api",
                    }
                ],
                "target_addresses": [
                    {
                        "name": "prod.polygon.open_close",
                        "address_type_name": "postgres",
                        "address_type_group_name": "database",
                    }
                ],
            },
            "default_watermark": "Default Watermark Value",
            "watermark": None,  # Will be set later
        }

With pipeline configuration in source control, we need to create a function 
that will sync the pipeline configuration with the Watcher framework by calling the 
``/pipeline`` endpoint.

.. code-block:: python

    import httpx

    base_url = "http://localhost:8000"

    def sync_pipeline_configuration(pipeline_config: dict):
        response = httpx.post(f"{base_url}/pipeline", json=pipeline_config["pipeline"])
        return response.json()


Watermark Management
~~~~~~~~~~~~~~~~~~~~

Calculating the next watermark can be pipeline specific, but we can modify our function to 
handle an input argument. 
I'd recommend adding a default watermark value to your pipeline configuration.

.. code-block:: python

    import httpx

    base_url = "http://localhost:8000"

    def sync_pipeline_configuration(pipeline_config: dict, next_watermark: Optional[str] = None):
        if next_watermark is not None:
            pipeline_config["pipeline"].next_watermark = next_watermark
        
        response = httpx.post(f"{base_url}/pipeline", json=pipeline_config["pipeline"])
        
        if response.json()["watermark"] is None:
            pipeline_config["watermark"] = pipeline_config["default_watermark"]

        return pipeline_config


Sync Address Lineage
~~~~~~~~~~~~~~~~~~~~

We can add logic to our function to sync the address lineage if load_lineage is True.

.. code-block:: python

    import httpx

    base_url = "http://localhost:8000"

    def sync_pipeline_configuration(pipeline_config: dict, next_watermark: Optional[str] = None):
        if next_watermark is not None:
            pipeline_config["pipeline"].next_watermark = next_watermark

        response = httpx.post(f"{base_url}/pipeline", json=pipeline_config["pipeline"])
        
        if response.json()["watermark"] is None:
            pipeline_config["watermark"] = pipeline_config["default_watermark"]

        # NEW CODE
        if response.json()["load_lineage"]:
            pipeline_config["lineage"]["pipeline_id"] = response.json()["id"]
            httpx.post(f"{base_url}/address_lineage", json=pipeline_config["lineage"])

        return pipeline_config

Pipeline Execution
~~~~~~~~~~~~~~~~~~

We can create a decorator function that will wrap around our ETL code to 
handle start / end pipeline execution.

.. code-block:: python

    import httpx

    base_url = "http://localhost:8000"

    def track_pipeline_execution(
        pipeline_id: int, parent_execution_id: Optional[int] = None
    ):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_execution = {
                    "pipeline_id": pipeline_id,
                    "start_date": pendulum.now("UTC").isoformat(),
                }
                if parent_execution_id is not None:
                    start_execution["parent_id"] = parent_execution_id

                start_response = httpx.post(
                    f"{base_url}/start_pipeline_execution", json=start_execution
                )
                execution_id = start_response.json()["id"]

                try:
                    result = func(*args, **kwargs)  # Runs the pipeline etl function

                    # MAKE SURE FUNCTION RETURNS A DICTIONARY 
                    # WITH END PIPELINE EXECUTION METRICS

                    result["id"] = execution_id
                    result["end_date"] = pendulum.now("UTC").isoformat()
                    result["completed_successfully"] = True

                    httpx.post(
                        f"{base_url}/end_pipeline_execution",
                        json=result,
                    )

                    return result

                except Exception as e:
                    failure_result = {
                        "id": execution_id,
                        "end_date": pendulum.now("UTC").isoformat(),
                        "completed_successfully": False,
                    }
                    httpx.post(
                        f"{base_url}/end_pipeline_execution",
                        json=failure_result,
                    )
                    raise e

            return wrapper

        return decorator

Example Implementation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pendulum
    from pipeline import PIPELINE_CONFIG
    from utils import sync_pipeline_configuration, track_pipeline_execution

    # Calculate next_watermark for your specific pipeline

    pipeline_config = sync_pipeline_configuration(PIPELINE_CONFIG, next_watermark)
    
    @track_pipeline_execution(pipeline_id=pipeline_config["id"], parent_execution_id=None)
    def etl_script(watermark: pendulum.date, next_watermark: pendulum.date):
        pass

    # Cast watermark / next_watermark if needed
    etl_script(pipeline_config["watermark"], pipeline_config["next_watermark"])


This is an advanced implementation that is recommended to simplify your code 
and allow for easy integration into the Watcher framework in a scalable way.
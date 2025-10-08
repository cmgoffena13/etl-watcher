ETL Example
===============

This section documents a complete ETL example in Python using Watcher 
and the Polygon API to extract stock market data.

Overview
~~~~~~~~~~~~

This example demonstrates a real-world ETL pipeline that:

- Extracts daily stock open/close data from the Polygon API
- Uses Watcher for pipeline execution tracking and metadata management
- Handles rate limiting and error scenarios
- Implements proper watermark management for incremental processing
- Creates address lineage relationships for data flow tracking

Complete Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's the complete working example:

.. code-block:: python

   import time

   import httpx
   import pendulum

   current_date = pendulum.now().date()
   pipeline = {
       "name": "polygon_open_close",
       "pipeline_type_name": "extraction",
       "next_watermark": current_date.to_date_string(),
   }

   response = httpx.post("http://localhost:8000/pipeline", json=pipeline)
   pipeline_id = response.json()["id"]
   watermark = response.json()["watermark"]
   print("Watermark:", watermark)
   load_lineage = response.json()["load_lineage"]

   default_watermark = pendulum.date(2025, 1, 1)
   if watermark is None:
       watermark = default_watermark
   else:
       watermark = pendulum.parse(watermark).date()

   if load_lineage:
       lineage = {
           "pipeline_id": pipeline_id,
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
       }
       httpx.post("http://localhost:8000/address_lineage", json=lineage)

   start_execution = {
       "pipeline_id": pipeline_id,
       "start_time": pendulum.now().isoformat(),
   }
   response = httpx.post("http://localhost:8000/start_pipeline_execution", json=start_execution)
   pipeline_execution_id = response.json()["id"]

   params = {
       "apiKey": "XXXX",
   }

   all_records = []
   try:
       while watermark < current_date:
           response = httpx.get(
               f"https://api.polygon.io/v1/open-close/AAPL/{watermark}", params=params
           )

           record = response.json()

           if response.status_code == 429:
               wait_time = 30
               print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
               time.sleep(wait_time)
               continue

           if record["status"] == "OK":
               all_records.append(record)
           watermark = watermark.add(days=1)

       print(all_records)  # Save records somewhere

       end_execution = {
           "id": pipeline_execution_id,
           "pipeline_id": pipeline_id,
           "end_date": pendulum.now().isoformat(),
           "completed_successfully": True,
           "total_rows": len(all_records),
       }
       httpx.post("http://localhost:8000/end_pipeline_execution", json=end_execution)
   except Exception as e:
       end_execution = {
           "id": pipeline_execution_id,
           "pipeline_id": pipeline_id,
           "end_date": pendulum.now().isoformat(),
           "completed_successfully": False,
       }
       httpx.post("http://localhost:8000/end_pipeline_execution", json=end_execution)
       raise e

Key Features Demonstrated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline Management:**

- **Get-or-Create Pattern**: No separate creation calls needed; pipeline and pipeline_type are automatically created if they don't exist
- **Watermark Processing**: Uses watermark-based incremental processing for efficient data extraction
- **Load Scenarios**: Handles both full load and incremental scenarios seamlessly
- **Easy Deployment**: Same code works for first run and subsequent runs without modification

**Address Lineage:**

- Creates source-to-target data lineage relationships
- Uses proper address naming conventions (API endpoint and database table)
- Automatically creates address types (polygon API, postgres database)

**Execution Tracking:**

- Proper start/end execution pattern with error handling
- Tracks execution metrics (total_rows processed)
- Handles both successful and failed execution scenarios

**Rate Limiting:**

- Implements proper rate limit handling with exponential backoff
- Continues processing after rate limit recovery
- Maintains data integrity during API throttling

**Watermark Management:**

- Uses date-based watermarks for incremental processing
- Handles initial watermark setup for new pipelines
- Advances watermark through date range processing

**Error Handling:**

- Comprehensive try/catch with proper execution cleanup
- Ensures execution is always ended, even on failure
- Maintains execution status accuracy

Best Practices Shown
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Source-Controlled Lineage** - Lineage definitions are in the pipeline code
2. **Proper Error Handling** - Always end execution, even on failure
3. **Rate Limit Management** - Graceful handling of API limitations
4. **Incremental Processing** - Efficient watermark-based data extraction
5. **Execution Metrics** - Tracking of rows processed for monitoring
6. **Address Naming** - Clear, descriptive address names for lineage tracking

This example demonstrates a production-ready-esque ETL pipeline that follows Watcher best practices for metadata management, execution tracking, and data lineage.


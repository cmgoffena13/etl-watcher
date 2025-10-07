Watermark Management
====================

This guide covers how to effectively manage watermarks in Watcher.

Understanding Watermarks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Watermarks track the progress of data processing in incremental data pipelines:

- **watermark** Current position (where processing has reached)
- **next_watermark** Target position (where processing should go to)

**Key Features:**

- **Incremental Processing**: Support for watermark-based incremental data pipelines
- **Flexible Watermarking**: Use any identifier (IDs, timestamps, etc.) as watermarks
- **Automatic Updates**: Watermarks are automatically updated after successful pipeline execution

Watermark Patterns
~~~~~~~~~~~~~~~~~~

Watermarks are stored as strings in the database. This allows for flexibility in the watermark format.

**Daily Processing**

.. code-block:: json

   {
     "watermark": "2024-01-01T00:00:00Z",
     "next_watermark": "2024-01-01T23:59:59Z"
   }

**Hourly Processing**

.. code-block:: json

   {
     "watermark": "2024-01-01T10:00:00Z",
     "next_watermark": "2024-01-01T11:00:00Z"
   }

**Numeric Watermarks**

.. code-block:: json

   {
     "watermark": "1000",
     "next_watermark": "2000"
   }

Watermark Increment Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After successful execution, the watermark is automatically updated:

1. **Execution completes successfully**
2. **Pipeline watermark becomes next_watermark**
3. **Next execution starts from the new watermark**

Example Flow:

.. code-block:: text

   Execution 1: watermark=0, next_watermark=1000 → Success → watermark=1000
   Execution 2: watermark=1000, next_watermark=2000 → Success → watermark=2000
   Execution 3: watermark=2000, next_watermark=3000 → Success → watermark=3000

.. note::
   It is critical that your pipeline logic properly handles inclusivity/exclusivity to 
   avoid overlapping watermark values. For example, if using ID-based watermarks, use 
   `WHERE id > watermark AND id <= next_watermark` to ensure no records are processed 
   twice or missed between executions.

How to Use Watermarks
~~~~~~~~~~~~~~~~~~~~~

To properly use watermarks in your pipeline, you need to: 

1. Calculate the next watermark
2. Use the next_watermark value in your pipeline call
3. Grab the watermark value from the pipeline response
4. To account for the first run of the pipeline (watermark None), you'll need a default starting value

Practical Example
~~~~~~~~~~~~~~~~~~

Here's a complete example of using watermarks in a pipeline:

.. code-block:: python

   # Step 1: Get the current watermark and determine next_watermark
   next_watermark = 150  # SELECT MAX(id) FROM your_table
   
   # Step 2: Create pipeline with next_watermark
   pipeline_data = {
       "name": "stock-price-worker",
       "pipeline_type_name": "api-integration",
       "full_load": False,
       "next_watermark": next_watermark  # Converted to string
   }

   pipeline_response = await client.post("/pipeline", json=pipeline_data)
   watermark = pipeline_response.json()['watermark']
   if watermark is None:
       watermark = 0
   else:
       watermark = int(watermark)

   # Step 3: Start pipeline execution
   execution_response = await client.post("/start_pipeline_execution", json={
       "pipeline_id": pipeline_result['id'],
       "start_date": pendulum.now("UTC").isoformat(),
       "full_load": False,
       "watermark": watermark,
       "next_watermark": max_id_from_source
   })
   
   # Step 4: Use watermarks in your data processing   
   # Process data using watermark boundaries
   SELECT *
   FROM Table_A
   WHERE id <= next_watermark
       AND id > watermark
   
   # Step 5: End execution (watermark automatically updated)
   await client.post("/end_pipeline_execution", json={
       "id": execution_id,
       "end_date": pendulum.now("UTC").isoformat(),
       "completed_successfully": True,
       "total_rows": 180
   })

**Important Notes:**

- Watermarks are automatically updated when `end_pipeline_execution` is called
- The system converts numeric watermarks to strings for storage
- Use `id > watermark AND id <= next_watermark` for proper boundary handling
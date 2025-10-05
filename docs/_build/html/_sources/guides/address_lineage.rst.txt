Address Lineage
====================

This guide covers how to effectively manage address lineage in Watcher.

Understanding Address Lineage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Address lineage tracks data flow relationships between sources and targets:

- **Address Management**: Track source and target data addresses with type classification
- **Lineage Relationships**: Create and maintain data flow relationships between sources and targets
- **Closure Table Pattern**: Efficient querying of complex lineage hierarchies with depth tracking
- **Source Control Integration**: Store lineage definitions in version control for reproducibility

Source-Controlled Lineage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Recommended Approach**: Store address lineage definitions directly in your pipeline code for version control and reproducibility.

**Benefits:**

- **Version Control**: Lineage definitions are tracked with your code changes
- **Reproducibility**: Lineage is automatically recreated when pipelines are deployed
- **Code Review**: Lineage changes are reviewed alongside code changes
- **Consistency**: Ensures lineage matches the actual data flow in your code

**Implementation Pattern:**

.. code-block:: python

   # In your pipeline code
   def run_pipeline():
       # Your data processing logic here
       
       # Define lineage relationships
       lineage_data = {
           "pipeline_id": pipeline_id,
           "source_addresses": [
               {
                   "name": "source_db.source_schema.source_raw_events",
                   "address_type_name": "postgresql",
                   "address_type_group_name": "database"
               }
           ],
           "target_addresses": [
               {
                   "name": "warehouse.schema.processed_events",
                   "address_type_name": "snowflake",
                   "address_type_group_name": "warehouse"
               }
           ]
       }
       
       # Create lineage relationships
       if pipeline_result['load_lineage']:
           lineage_response = requests.post(
               "http://localhost:8000/address_lineage",
               json=lineage_data
           )
           print(f"Lineage created: {lineage_response.json()}")

**Best Practices:**

- **Store in Pipeline**: Keep lineage definitions in the same file as your pipeline logic
- **Use Variables**: Reference pipeline_id and other dynamic values
- **Check load_lineage**: Only create lineage when the flag is enabled
- **Document Changes**: Include lineage changes in your commit messages

Creating Lineage Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track relationships between data sources:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         lineage_data = {
             "pipeline_id": 1,
             "source_addresses": [
                 {
                     "name": "source_db.stock_prices",
                     "address_type_name": "postgresql",
                     "address_type_group_name": "database"
                 }
             ],
             "target_addresses": [
                 {
                     "name": "warehouse.stock_prices",
                     "address_type_name": "postgresql",
                     "address_type_group_name": "database"
                 }
             ]
         }

         response = requests.post(
             "http://localhost:8000/address_lineage",
             json=lineage_data
         )
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         lineage_data = {
             "pipeline_id": 1,
             "source_addresses": [
                 {
                     "name": "source_db.stock_prices",
                     "address_type_name": "postgresql",
                     "address_type_group_name": "database"
                 }
             ],
             "target_addresses": [
                 {
                     "name": "warehouse.stock_prices",
                     "address_type_name": "postgresql",
                     "address_type_group_name": "database"
                 }
             ]
         }

         with httpx.Client() as client:
             response = client.post(
                 "http://localhost:8000/address_lineage",
                 json=lineage_data
             )
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X POST "http://localhost:8000/address_lineage" \
              -H "Content-Type: application/json" \
              -d '{
                "pipeline_id": 1,
                "source_addresses": [
                  {
                    "name": "source_db.stock_prices",
                    "address_type_name": "postgresql",
                    "address_type_group_name": "database"
                  }
                ],
                "target_addresses": [
                  {
                    "name": "warehouse.stock_prices",
                    "address_type_name": "postgresql",
                    "address_type_group_name": "database"
                  }
                ]
              }'

   .. tab:: HTTPie

      .. code-block:: bash

         http POST localhost:8000/address_lineage \
              pipeline_id=1 \
              source_addresses:='[{"name": "source_db.stock_prices", "address_type_name": "postgresql", "address_type_group_name": "database"}]' \
              target_addresses:='[{"name": "warehouse.stock_prices", "address_type_name": "postgresql", "address_type_group_name": "database"}]'

Querying Lineage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get lineage information for an address:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         response = requests.get("http://localhost:8000/address_lineage/1")
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         with httpx.Client() as client:
             response = client.get("http://localhost:8000/address_lineage/1")
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X GET "http://localhost:8000/address_lineage/1"

   .. tab:: HTTPie

      .. code-block:: bash

         http GET localhost:8000/address_lineage/1

**Response:**

.. code-block:: json

   [
     {
       "source_address_id": 1,
       "target_address_id": 2,
       "depth": 1,
       "source_address_name": "raw_sales_data",
       "target_address_name": "processed_sales_data"
     }
   ]

Closure Table Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Address lineage uses a closure table pattern for efficient querying of complex lineage hierarchies:

**How It Works:**

- **Direct Relationships**: Stores immediate parent-child relationships in `address_lineage`
- **Closure Table**: Maintains all ancestor-descendant relationships in `address_lineage_closure`
- **Depth Tracking**: Records the depth of each relationship for hierarchical queries
- **Automatic Maintenance**: Background Celery task keeps closure table synchronized

**Background Task:**

The `address_lineage_closure_rebuild_task` automatically maintains the closure table:

- **Rate Limit**: 1 request per second
- **Trigger**: Runs when new lineage relationships are created
- **Purpose**: Rebuilds all ancestor-descendant relationships
- **Performance**: Enables efficient queries across complex lineage hierarchies

**Benefits:**

- **Fast Queries**: O(1) lookup for any ancestor-descendant relationship
- **Depth Support**: Easy querying by relationship depth
- **Hierarchical Views**: Complete lineage trees in single queries
- **Automatic Updates**: No manual maintenance required

**Example Query:**

Find all descendants of a source address at any depth:

.. code-block:: sql

   SELECT target_address_id, depth
   FROM address_lineage_closure
   WHERE source_address_id = 1
   ORDER BY depth;

Pipeline Integration
~~~~~~~~~~~~~~~~~~~~

Address lineage is commonly used in pipeline workflows. Here's how to integrate it:

.. code-block:: python

   # Check if pipeline has load_lineage enabled
   if pipeline_result['load_lineage']:
       lineage_data = {
           "pipeline_id": pipeline_result['id'],
           "source_addresses": [
               {
                   "name": "source_db.stock_prices",
                   "address_type_name": "postgresql",
                   "address_type_group_name": "database"
               }
           ],
           "target_addresses": [
               {
                   "name": "warehouse.stock_prices",
                   "address_type_name": "postgresql",
                   "address_type_group_name": "database"
               }
           ]
       }
       
       lineage_response = await client.post(
           "http://localhost:8000/address_lineage",
           json=lineage_data
       )
       lineage_result = lineage_response.json()
       print(f"Lineage relationships created: {lineage_result['lineage_relationships_created']}")

**Key Features:**

- **Automatic Reset**: `load_lineage` automatically resets to `False` after execution
- **Source Control**: Lineage definitions can be stored in version control
- **Efficient Queries**: Uses closure table pattern for complex lineage hierarchies
- **Depth Tracking**: Tracks relationship depth for hierarchical data flows

Managing Load Lineage Flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `load_lineage` flag controls when lineage relationships are created:

- **Default Behavior**: `load_lineage` is `True` when a pipeline is first created
- **Automatic Reset**: After successful execution, `load_lineage` automatically resets to `False`
- **Manual Control**: You can manually set `load_lineage` to `True` to force lineage creation

Update a pipeline's load_lineage flag:

.. tabs::

   .. tab:: Python - requests

      .. code-block:: python

         import requests

         # Update pipeline to enable lineage loading
         pipeline_update = {
             "id": 1,
             "load_lineage": True
         }

         response = requests.patch(
             "http://localhost:8000/pipeline",
             json=pipeline_update
         )
         print(response.json())

   .. tab:: Python - httpx

      .. code-block:: python

         import httpx

         # Update pipeline to enable lineage loading
         pipeline_update = {
             "id": 1,
             "load_lineage": True
         }

         with httpx.Client() as client:
             response = client.patch(
                 "http://localhost:8000/pipeline",
                 json=pipeline_update
             )
             print(response.json())

   .. tab:: curl

      .. code-block:: bash

         curl -X PATCH "http://localhost:8000/pipeline" \
              -H "Content-Type: application/json" \
              -d '{
                "id": 1,
                "load_lineage": true
              }'

   .. tab:: HTTPie

      .. code-block:: bash

         http PATCH localhost:8000/pipeline \
              id=1 \
              load_lineage=true

**Use Cases:**

- **Initial Setup**: Set `load_lineage=True` when first creating lineage relationships
- **Schema Changes**: Re-enable when data sources or targets change
- **Reprocessing**: Force lineage recreation for data quality or compliance
- **Development**: Enable for testing lineage relationships

.. note::
   Remember that `load_lineage` will automatically reset to `False` after the next successful pipeline execution, so you'll need to set it to `True` again if you want to recreate lineage relationships in subsequent runs.

Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Effective organization of your Watcher metadata is crucial for maintainability, monitoring, and team collaboration.

**General Best Practices:**

1. **Consistency**: Use the same naming patterns across all teams and projects
2. **Descriptiveness**: Names should clearly indicate purpose and scope
3. **Hierarchy**: Use underscores to create logical hierarchies
4. **Future-Proofing**: Choose names that will remain relevant as systems evolve
5. **Documentation**: Document your naming conventions and share with all teams
6. **Validation**: Implement naming validation in your CI/CD pipeline or code reviews

Address Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Addresses should be the actual, usable path/URL that you would use to access the data:

**Examples:**

- `gs://my-bucket/raw/events/2024/01/09/` - GCS bucket path for raw events
- `https://api.example.com/v1/customers` - REST API endpoint for customers
- `analytics.public.users` - database table
- `topic-name` - Kafka topic with broker info

**Best Practices:**

- Use the URL format for the system
- Be specific enough that someone could use the address to access the data given the address type context
- Use standard formats for each system type (Bucket URLs, HTTP endpoints, database.schema.table)

Address Type Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Categorize addresses by their technical characteristics:

**Group Names:**

- `database` - Database systems (PostgreSQL, MySQL, etc.)
- `warehouse` - Data warehouses (Snowflake, BigQuery, etc.)
- `bucket` - Data lakes (S3, ADLS, etc.)
- `api` - API endpoints and services
- `file` - File systems and storage
- `stream` - Streaming data sources
- `dashboard` - Dashboard targets

**Type Names:**

- `postgresql` - PostgreSQL databases
- `snowflake` - Snowflake data warehouse
- `s3` - Amazon S3 buckets
- `kafka` - Kafka topics
- `looker` - Looker dashboard

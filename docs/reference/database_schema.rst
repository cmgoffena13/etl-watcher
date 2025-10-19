Database Schema
===============

This section documents the complete database schema for Watcher.

Core Tables
-----------

Pipeline
~~~~~~~~

Primary pipeline configuration table.

.. code-block:: sql

   CREATE TABLE pipeline (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       pipeline_type_id INTEGER NOT NULL REFERENCES pipeline_type(id),
       watermark VARCHAR(50) NULL,
       next_watermark VARCHAR(50) NULL,
       pipeline_metadata JSONB NULL,
       last_target_insert TIMESTAMP WITH TIME ZONE NULL,
       last_target_update TIMESTAMP WITH TIME ZONE NULL,
       last_target_soft_delete TIMESTAMP WITH TIME ZONE NULL,
       freshness_number INTEGER NULL,
       freshness_datepart VARCHAR(20) NULL,
       mute_freshness_check BOOLEAN DEFAULT FALSE NOT NULL,
       timeliness_number INTEGER NULL,
       timeliness_datepart VARCHAR(20) NULL,
       mute_timeliness_check BOOLEAN DEFAULT FALSE NOT NULL,
       load_lineage BOOLEAN DEFAULT TRUE NOT NULL,
       active BOOLEAN DEFAULT TRUE NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE NULL
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_pipeline_name_include ON pipeline (name) INCLUDE (load_lineage, active, id);
   CREATE INDEX ix_pipeline_pipeline_type_id_include ON pipeline (pipeline_type_id) INCLUDE (id);

Pipeline Type
~~~~~~~~~~~~~~

Pipeline type classification.

.. code-block:: sql

   CREATE TABLE pipeline_type (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       freshness_number INTEGER NULL,
       freshness_datepart VARCHAR(20) NULL,
       mute_freshness_check BOOLEAN DEFAULT FALSE NOT NULL,
       timeliness_number INTEGER NULL,
       timeliness_datepart VARCHAR(20) NULL,
       mute_timeliness_check BOOLEAN DEFAULT FALSE NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE NULL
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_pipeline_type_name_include ON pipeline_type (name) INCLUDE (id);

Pipeline Execution
~~~~~~~~~~~~~~~~~~

Pipeline execution tracking.

.. code-block:: sql

   CREATE TABLE pipeline_execution (
       id BIGINT PRIMARY KEY,
       parent_id BIGINT NULL REFERENCES pipeline_execution(id),
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       start_date TIMESTAMP WITH TIME ZONE NOT NULL,
       date_recorded DATE NOT NULL,
       hour_recorded INTEGER NOT NULL,
       end_date TIMESTAMP WITH TIME ZONE NULL,
       duration_seconds INTEGER NULL,
       completed_successfully BOOLEAN NULL,
       inserts INTEGER NULL CHECK (inserts >= 0),
       updates INTEGER NULL CHECK (updates >= 0),
       soft_deletes INTEGER NULL CHECK (soft_deletes >= 0),
       total_rows INTEGER NULL CHECK (total_rows >= 0),
       watermark VARCHAR(50) NULL,
       next_watermark VARCHAR(50) NULL,
       execution_metadata JSONB NULL,
       anomaly_flags JSONB NULL,
       throughput DECIMAL(12,4) NULL,
       
       -- Constraints
       CONSTRAINT check_end_after_start CHECK (end_date IS NULL OR end_date > start_date),
       CONSTRAINT check_parent_not_self CHECK (parent_id IS NULL OR parent_id != id)
   );
   
   -- Indexes
   CREATE INDEX ix_pipeline_execution_start_date ON pipeline_execution (start_date) INCLUDE (id);
   CREATE INDEX ix_pipeline_execution_hour_recorded ON pipeline_execution (pipeline_id, hour_recorded, end_date) 
       INCLUDE (completed_successfully, id) WHERE end_date IS NOT NULL;
   CREATE INDEX ix_pipeline_execution_date_recorded_seek ON pipeline_execution (date_recorded, pipeline_id) INCLUDE (id);

Pipeline Execution Closure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hierarchical pipeline execution relationships.

.. code-block:: sql

   CREATE TABLE pipeline_execution_closure (
       parent_execution_id BIGINT NOT NULL,
       child_execution_id BIGINT NOT NULL,
       depth INTEGER NOT NULL,
       PRIMARY KEY (parent_execution_id, child_execution_id),
       FOREIGN KEY (parent_execution_id) REFERENCES pipeline_execution(id),
       FOREIGN KEY (child_execution_id) REFERENCES pipeline_execution(id)
   );
   
   -- Indexes
   CREATE INDEX ix_pipeline_execution_closure_depth_parent_include ON pipeline_execution_closure (parent_execution_id, depth) INCLUDE (child_execution_id);
   CREATE INDEX ix_pipeline_execution_closure_depth_child_include ON pipeline_execution_closure (child_execution_id, depth) INCLUDE (parent_execution_id);

Address
~~~~~~~

Data address tracking.

.. code-block:: sql

   CREATE TABLE address (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       address_type_id INTEGER NOT NULL REFERENCES address_type(id),
       database_name VARCHAR(50) NULL,
       schema_name VARCHAR(50) NULL,
       table_name VARCHAR(50) NULL,
       primary_key VARCHAR(50) NULL,
       address_metadata JSONB NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE NULL
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_address_name_include ON address (name) INCLUDE (id);

Address Type
~~~~~~~~~~~~~

Address type classification.

.. code-block:: sql

   CREATE TABLE address_type (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       group_name VARCHAR(150) NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE NULL
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_address_type_name_include ON address_type (name) INCLUDE (id);

Address Lineage
~~~~~~~~~~~~~~~

Data lineage relationships.

.. code-block:: sql

   CREATE TABLE address_lineage (
       id BIGINT PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       source_address_id INTEGER NOT NULL REFERENCES address(id),
       target_address_id INTEGER NOT NULL REFERENCES address(id)
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_address_lineage_source_target ON address_lineage (source_address_id, target_address_id);
   CREATE UNIQUE INDEX ux_address_lineage_target_source ON address_lineage (target_address_id, source_address_id);
   CREATE INDEX ix_address_lineage_pipeline_id ON address_lineage (pipeline_id);

Address Lineage Closure
~~~~~~~~~~~~~~~~~~~~~~~~

Transitive closure of address lineage relationships.

.. code-block:: sql

   CREATE TABLE address_lineage_closure (
       source_address_id INTEGER NOT NULL,
       target_address_id INTEGER NOT NULL,
       depth INTEGER NOT NULL,
       lineage_path INTEGER[] NOT NULL,
       PRIMARY KEY (source_address_id, target_address_id),
       FOREIGN KEY (source_address_id) REFERENCES address(id),
       FOREIGN KEY (target_address_id) REFERENCES address(id)
   );
   
   -- Indexes
   CREATE INDEX ix_address_lineage_closure_depth_source_include ON address_lineage_closure (source_address_id, depth) INCLUDE (target_address_id);
   CREATE INDEX ix_address_lineage_closure_depth_target_include ON address_lineage_closure (target_address_id, depth) INCLUDE (source_address_id);

Monitoring Tables
-----------------

Timeliness Pipeline Execution Log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timeliness monitoring results.

.. code-block:: sql

   CREATE TABLE timeliness_pipeline_execution_log (
       pipeline_execution_id BIGINT PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       duration_seconds INTEGER NOT NULL,
       seconds_threshold INTEGER NOT NULL,
       execution_status VARCHAR(50) NOT NULL,
       timely_number INTEGER NOT NULL,
       timely_datepart VARCHAR(20) NOT NULL,
       used_child_config BOOLEAN NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       FOREIGN KEY (pipeline_execution_id) REFERENCES pipeline_execution(id)
   );

Freshness Pipeline Log
~~~~~~~~~~~~~~~~~~~~~~~~

Freshness monitoring results.

.. code-block:: sql

   CREATE TABLE freshness_pipeline_log (
       id BIGINT PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       last_dml_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
       evaluation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
       freshness_number INTEGER NOT NULL,
       freshness_datepart VARCHAR(20) NOT NULL,
       used_child_config BOOLEAN NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
   );
   
   -- Indexes
   CREATE UNIQUE INDEX ux_freshness_pipeline_log ON freshness_pipeline_log (last_dml_timestamp, pipeline_id);

Anomaly Detection
-----------------

Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~~

Anomaly detection configuration.

.. code-block:: sql

   CREATE TABLE anomaly_detection_rule (
       id SERIAL PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       metric_field VARCHAR(50) NOT NULL,
       z_threshold DECIMAL(4,2) DEFAULT 3.0 NOT NULL,
       lookback_days INTEGER DEFAULT 30 NOT NULL,
       minimum_executions INTEGER DEFAULT 30 NOT NULL,
       active BOOLEAN DEFAULT TRUE NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE NULL
   );
   
   -- Indexes
   CREATE INDEX ix_anomaly_detection_rule_pipeline_id_include ON anomaly_detection_rule (pipeline_id, active) INCLUDE (id);
   CREATE UNIQUE INDEX ux_anomaly_detection_rule_composite_key_include ON anomaly_detection_rule (pipeline_id, metric_field) INCLUDE (id);

Anomaly Detection Result
~~~~~~~~~~~~~~~~~~~~~~~~~

Anomaly detection results.

.. code-block:: sql

   CREATE TABLE anomaly_detection_result (
       pipeline_execution_id BIGINT NOT NULL,
       rule_id INTEGER NOT NULL REFERENCES anomaly_detection_rule(id),
       violation_value DECIMAL(12,4) NOT NULL,
       z_score DECIMAL(12,4) NOT NULL,
       historical_mean DECIMAL(12,4) NOT NULL,
       std_deviation_value DECIMAL(12,4) NOT NULL,
       z_threshold DECIMAL(12,4) NOT NULL,
       threshold_min_value DECIMAL(12,4) NOT NULL,
       threshold_max_value DECIMAL(12,4) NOT NULL,
       context JSONB NULL,
       detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
       PRIMARY KEY (pipeline_execution_id, rule_id),
       FOREIGN KEY (pipeline_execution_id) REFERENCES pipeline_execution(id)
   );

Data Relationships
-------------------

Hierarchical Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline Execution Hierarchy**

- Parent-child relationships via `parent_id`
- Closure table for efficient parent/child queries
- Depth tracking for relationship levels

**Address Lineage Hierarchy**

- Source-target relationships via `source_address_id` and `target_address_id`
- Closure table for transitive relationships
- Depth tracking for lineage levels

Many-to-Many Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline-Address Relationships**

- Pipelines can have multiple addresses
- Addresses can be used by multiple pipelines
- Junction table: `address_lineage`

**Pipeline-Execution Relationships**

- Pipelines can have multiple executions
- Executions belong to one pipeline
- Foreign key: `pipeline_id`

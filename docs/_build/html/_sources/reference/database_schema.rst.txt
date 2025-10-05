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
       watermark VARCHAR(255),
       next_watermark VARCHAR(255),
       active BOOLEAN DEFAULT true,
       load_lineage BOOLEAN DEFAULT true,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       pipeline_metadata JSONB,
       freshness_number INTEGER CHECK (freshness_number > 0),
       freshness_datepart VARCHAR(20) CHECK (freshness_datepart IN ('hour', 'day', 'week', 'month', 'quarter', 'year')),
       mute_freshness_check BOOLEAN DEFAULT false,
       timeliness_number INTEGER CHECK (timeliness_number > 0),
       timeliness_datepart VARCHAR(20) CHECK (timeliness_datepart IN ('hour', 'day', 'week', 'month', 'quarter', 'year')),
       mute_timeliness_check BOOLEAN DEFAULT false
   );

Pipeline Type
~~~~~~~~~~~~~

Pipeline type classification.

.. code-block:: sql

   CREATE TABLE pipeline_type (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       group_name VARCHAR(150) NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(name, group_name)
   );

Pipeline Execution
~~~~~~~~~~~~~~~~~~

Pipeline execution tracking.

.. code-block:: sql

   CREATE TABLE pipeline_execution (
       id SERIAL PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       start_date TIMESTAMP WITH TIME ZONE NOT NULL,
       end_date TIMESTAMP WITH TIME ZONE,
       completed_successfully BOOLEAN,
       total_rows INTEGER CHECK (total_rows >= 0),
       inserts INTEGER CHECK (inserts >= 0),
       updates INTEGER CHECK (updates >= 0),
       soft_deletes INTEGER CHECK (soft_deletes >= 0),
       duration_seconds DECIMAL(10,2),
       throughput DECIMAL(10,2),
       parent_id INTEGER REFERENCES pipeline_execution(id),
       execution_metadata JSONB,
       anomaly_flags JSONB,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

Pipeline Execution Closure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Hierarchical pipeline execution relationships.

.. code-block:: sql

   CREATE TABLE pipeline_execution_closure (
       ancestor_id BIGINT NOT NULL REFERENCES pipeline_execution(id),
       descendant_id BIGINT NOT NULL REFERENCES pipeline_execution(id),
       depth INTEGER NOT NULL,
       PRIMARY KEY (ancestor_id, descendant_id),
       FOREIGN KEY (ancestor_id) REFERENCES pipeline_execution(id),
       FOREIGN KEY (descendant_id) REFERENCES pipeline_execution(id)
   );

Address
~~~~~~~

Data address tracking.

.. code-block:: sql

   CREATE TABLE address (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       address_type_id INTEGER NOT NULL REFERENCES address_type(id),
       watermark VARCHAR(255),
       active BOOLEAN DEFAULT true,
       load_lineage BOOLEAN DEFAULT true,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(name, address_type_id)
   );

Address Type
~~~~~~~~~~~~

Address type classification.

.. code-block:: sql

   CREATE TABLE address_type (
       id SERIAL PRIMARY KEY,
       name VARCHAR(150) NOT NULL,
       group_name VARCHAR(150) NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(name, group_name)
   );

Address Lineage
~~~~~~~~~~~~~~~

Data lineage relationships.

.. code-block:: sql

   CREATE TABLE address_lineage (
       id SERIAL PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       source_address_id INTEGER NOT NULL REFERENCES address(id),
       target_address_id INTEGER NOT NULL REFERENCES address(id),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(pipeline_id, source_address_id, target_address_id)
   );

Address Lineage Closure
~~~~~~~~~~~~~~~~~~~~~~~

Transitive closure of address lineage relationships.

.. code-block:: sql

   CREATE TABLE address_lineage_closure (
       source_address_id INTEGER NOT NULL REFERENCES address(id),
       target_address_id INTEGER NOT NULL REFERENCES address(id),
       depth INTEGER NOT NULL,
       PRIMARY KEY (source_address_id, target_address_id),
       FOREIGN KEY (source_address_id) REFERENCES address(id),
       FOREIGN KEY (target_address_id) REFERENCES address(id)
   );

Monitoring Tables
-----------------

Timeliness Pipeline Execution Log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timeliness monitoring results.

.. code-block:: sql

   CREATE TABLE timeliness_pipeline_execution_log (
       id SERIAL PRIMARY KEY,
       pipeline_execution_id INTEGER NOT NULL REFERENCES pipeline_execution(id),
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       execution_date TIMESTAMP WITH TIME ZONE NOT NULL,
       duration_seconds DECIMAL(10,2) NOT NULL,
       threshold_seconds DECIMAL(10,2) NOT NULL,
       is_timely BOOLEAN NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

Freshness Pipeline Log
~~~~~~~~~~~~~~~~~~~~~~

Freshness monitoring results.

.. code-block:: sql

   CREATE TABLE freshness_pipeline_log (
       id SERIAL PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       address_id INTEGER NOT NULL REFERENCES address(id),
       last_modified TIMESTAMP WITH TIME ZONE NOT NULL,
       threshold_hours INTEGER NOT NULL,
       is_fresh BOOLEAN NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

Anomaly Detection
-----------------

Anomaly Detection Rule
~~~~~~~~~~~~~~~~~~~~~~

Anomaly detection configuration.

.. code-block:: sql

   CREATE TABLE anomaly_detection_rule (
       id SERIAL PRIMARY KEY,
       pipeline_id INTEGER NOT NULL REFERENCES pipeline(id),
       metric_field VARCHAR(50) NOT NULL CHECK (metric_field IN ('total_rows', 'duration_seconds', 'throughput', 'inserts', 'updates', 'soft_deletes')),
       z_threshold DECIMAL(5,2) NOT NULL CHECK (z_threshold > 0),
       minimum_executions INTEGER NOT NULL CHECK (minimum_executions >= 2),
       active BOOLEAN DEFAULT true,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

Anomaly Detection Result
~~~~~~~~~~~~~~~~~~~~~~~

Anomaly detection results.

.. code-block:: sql

   CREATE TABLE anomaly_detection_result (
       id SERIAL PRIMARY KEY,
       rule_id INTEGER NOT NULL REFERENCES anomaly_detection_rule(id),
       pipeline_execution_id INTEGER NOT NULL REFERENCES pipeline_execution(id),
       violation_value DECIMAL(15,2) NOT NULL,
       z_score DECIMAL(10,4) NOT NULL,
       historical_mean DECIMAL(15,2) NOT NULL,
       std_deviation_value DECIMAL(15,2) NOT NULL,
       z_threshold DECIMAL(5,2) NOT NULL,
       threshold_min_value DECIMAL(15,2) NOT NULL,
       threshold_max_value DECIMAL(15,2) NOT NULL,
       context JSONB,
       detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

Indexes
-------

Performance Indexes
~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Pipeline indexes
   CREATE INDEX ix_pipeline_name ON pipeline(name);
   CREATE INDEX ix_pipeline_pipeline_type_id ON pipeline(pipeline_type_id);
   CREATE INDEX ix_pipeline_active ON pipeline(active);
   
   -- Pipeline execution indexes
   CREATE INDEX ix_pipeline_execution_pipeline_id ON pipeline_execution(pipeline_id);
   CREATE INDEX ix_pipeline_execution_start_date ON pipeline_execution(start_date);
   CREATE INDEX ix_pipeline_execution_end_date ON pipeline_execution(end_date);
   CREATE INDEX ix_pipeline_execution_completed_successfully ON pipeline_execution(completed_successfully);
   CREATE INDEX ix_pipeline_execution_parent_id ON pipeline_execution(parent_id);
   
   -- Address indexes
   CREATE INDEX ix_address_name ON address(name);
   CREATE INDEX ix_address_address_type_id ON address(address_type_id);
   CREATE INDEX ix_address_active ON address(active);
   
   -- Address lineage indexes
   CREATE INDEX ix_address_lineage_pipeline_id ON address_lineage(pipeline_id);
   CREATE INDEX ix_address_lineage_source_address_id ON address_lineage(source_address_id);
   CREATE INDEX ix_address_lineage_target_address_id ON address_lineage(target_address_id);
   
   -- Monitoring indexes
   CREATE INDEX ix_timeliness_pipeline_execution_log_pipeline_id ON timeliness_pipeline_execution_log(pipeline_id);
   CREATE INDEX ix_timeliness_pipeline_execution_log_execution_date ON timeliness_pipeline_execution_log(execution_date);
   CREATE INDEX ix_freshness_pipeline_log_pipeline_id ON freshness_pipeline_log(pipeline_id);
   CREATE INDEX ix_freshness_pipeline_log_address_id ON freshness_pipeline_log(address_id);
   
   -- Anomaly detection indexes
   CREATE INDEX ix_anomaly_detection_rule_pipeline_id ON anomaly_detection_rule(pipeline_id);
   CREATE INDEX ix_anomaly_detection_rule_active ON anomaly_detection_rule(active);
   CREATE INDEX ix_anomaly_detection_result_rule_id ON anomaly_detection_result(rule_id);
   CREATE INDEX ix_anomaly_detection_result_pipeline_execution_id ON anomaly_detection_result(pipeline_execution_id);
   CREATE INDEX ix_anomaly_detection_result_detected_at ON anomaly_detection_result(detected_at);

Composite Indexes
~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Pipeline execution composite indexes
   CREATE INDEX ix_pipeline_execution_pipeline_start_date ON pipeline_execution(pipeline_id, start_date);
   CREATE INDEX ix_pipeline_execution_pipeline_completed ON pipeline_execution(pipeline_id, completed_successfully);
   CREATE INDEX ix_pipeline_execution_parent_completed ON pipeline_execution(parent_id, completed_successfully);
   
   -- Address lineage composite indexes
   CREATE INDEX ix_address_lineage_pipeline_source ON address_lineage(pipeline_id, source_address_id);
   CREATE INDEX ix_address_lineage_pipeline_target ON address_lineage(pipeline_id, target_address_id);
   
   -- Monitoring composite indexes
   CREATE INDEX ix_timeliness_pipeline_execution_log_pipeline_execution ON timeliness_pipeline_execution_log(pipeline_id, execution_date);
   CREATE INDEX ix_freshness_pipeline_log_pipeline_address ON freshness_pipeline_log(pipeline_id, address_id);
   
   -- Anomaly detection composite indexes
   CREATE INDEX ix_anomaly_detection_rule_pipeline_active ON anomaly_detection_rule(pipeline_id, active);
   CREATE INDEX ix_anomaly_detection_result_rule_execution ON anomaly_detection_result(rule_id, pipeline_execution_id);

Covering Indexes
~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Pipeline execution covering indexes
   CREATE INDEX ix_pipeline_execution_pipeline_start_end ON pipeline_execution(pipeline_id, start_date, end_date) INCLUDE (completed_successfully, duration_seconds);
   CREATE INDEX ix_pipeline_execution_pipeline_completed_start ON pipeline_execution(pipeline_id, completed_successfully, start_date) INCLUDE (end_date, duration_seconds);
   
   -- Address lineage covering indexes
   CREATE INDEX ix_address_lineage_pipeline_source_target ON address_lineage(pipeline_id, source_address_id, target_address_id) INCLUDE (id);
   
   -- Monitoring covering indexes
   CREATE INDEX ix_timeliness_pipeline_execution_log_pipeline_execution_date ON timeliness_pipeline_execution_log(pipeline_id, execution_date) INCLUDE (duration_seconds, threshold_seconds, is_timely);
   CREATE INDEX ix_freshness_pipeline_log_pipeline_address_modified ON freshness_pipeline_log(pipeline_id, address_id, last_modified) INCLUDE (threshold_hours, is_fresh);

Partial Indexes
~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Active pipelines only
   CREATE INDEX ix_pipeline_active_true ON pipeline(pipeline_type_id) WHERE active = true;
   
   -- Completed executions only
   CREATE INDEX ix_pipeline_execution_completed_true ON pipeline_execution(pipeline_id, start_date) WHERE completed_successfully = true;
   
   -- Active addresses only
   CREATE INDEX ix_address_active_true ON address(address_type_id) WHERE active = true;
   
   -- Active anomaly detection rules only
   CREATE INDEX ix_anomaly_detection_rule_active_true ON anomaly_detection_rule(pipeline_id, metric_field) WHERE active = true;

Constraints
-----------

Primary Key Constraints
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Primary keys
   ALTER TABLE pipeline ADD CONSTRAINT pk_pipeline PRIMARY KEY (id);
   ALTER TABLE pipeline_type ADD CONSTRAINT pk_pipeline_type PRIMARY KEY (id);
   ALTER TABLE pipeline_execution ADD CONSTRAINT pk_pipeline_execution PRIMARY KEY (id);
   ALTER TABLE pipeline_execution_closure ADD CONSTRAINT pk_pipeline_execution_closure PRIMARY KEY (ancestor_id, descendant_id);
   ALTER TABLE address ADD CONSTRAINT pk_address PRIMARY KEY (id);
   ALTER TABLE address_type ADD CONSTRAINT pk_address_type PRIMARY KEY (id);
   ALTER TABLE address_lineage ADD CONSTRAINT pk_address_lineage PRIMARY KEY (id);
   ALTER TABLE address_lineage_closure ADD CONSTRAINT pk_address_lineage_closure PRIMARY KEY (source_address_id, target_address_id);
   ALTER TABLE timeliness_pipeline_execution_log ADD CONSTRAINT pk_timeliness_pipeline_execution_log PRIMARY KEY (id);
   ALTER TABLE freshness_pipeline_log ADD CONSTRAINT pk_freshness_pipeline_log PRIMARY KEY (id);
   ALTER TABLE anomaly_detection_rule ADD CONSTRAINT pk_anomaly_detection_rule PRIMARY KEY (id);
   ALTER TABLE anomaly_detection_result ADD CONSTRAINT pk_anomaly_detection_result PRIMARY KEY (id);

Foreign Key Constraints
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Pipeline foreign keys
   ALTER TABLE pipeline ADD CONSTRAINT fk_pipeline_pipeline_type FOREIGN KEY (pipeline_type_id) REFERENCES pipeline_type(id);
   
   -- Pipeline execution foreign keys
   ALTER TABLE pipeline_execution ADD CONSTRAINT fk_pipeline_execution_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id);
   ALTER TABLE pipeline_execution ADD CONSTRAINT fk_pipeline_execution_parent FOREIGN KEY (parent_id) REFERENCES pipeline_execution(id);
   
   -- Pipeline execution closure foreign keys
   ALTER TABLE pipeline_execution_closure ADD CONSTRAINT fk_pipeline_execution_closure_ancestor FOREIGN KEY (ancestor_id) REFERENCES pipeline_execution(id);
   ALTER TABLE pipeline_execution_closure ADD CONSTRAINT fk_pipeline_execution_closure_descendant FOREIGN KEY (descendant_id) REFERENCES pipeline_execution(id);
   
   -- Address foreign keys
   ALTER TABLE address ADD CONSTRAINT fk_address_address_type FOREIGN KEY (address_type_id) REFERENCES address_type(id);
   
   -- Address lineage foreign keys
   ALTER TABLE address_lineage ADD CONSTRAINT fk_address_lineage_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id);
   ALTER TABLE address_lineage ADD CONSTRAINT fk_address_lineage_source FOREIGN KEY (source_address_id) REFERENCES address(id);
   ALTER TABLE address_lineage ADD CONSTRAINT fk_address_lineage_target FOREIGN KEY (target_address_id) REFERENCES address(id);
   
   -- Address lineage closure foreign keys
   ALTER TABLE address_lineage_closure ADD CONSTRAINT fk_address_lineage_closure_source FOREIGN KEY (source_address_id) REFERENCES address(id);
   ALTER TABLE address_lineage_closure ADD CONSTRAINT fk_address_lineage_closure_target FOREIGN KEY (target_address_id) REFERENCES address(id);
   
   -- Monitoring foreign keys
   ALTER TABLE timeliness_pipeline_execution_log ADD CONSTRAINT fk_timeliness_pipeline_execution_log_pipeline_execution FOREIGN KEY (pipeline_execution_id) REFERENCES pipeline_execution(id);
   ALTER TABLE timeliness_pipeline_execution_log ADD CONSTRAINT fk_timeliness_pipeline_execution_log_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id);
   ALTER TABLE freshness_pipeline_log ADD CONSTRAINT fk_freshness_pipeline_log_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id);
   ALTER TABLE freshness_pipeline_log ADD CONSTRAINT fk_freshness_pipeline_log_address FOREIGN KEY (address_id) REFERENCES address(id);
   
   -- Anomaly detection foreign keys
   ALTER TABLE anomaly_detection_rule ADD CONSTRAINT fk_anomaly_detection_rule_pipeline FOREIGN KEY (pipeline_id) REFERENCES pipeline(id);
   ALTER TABLE anomaly_detection_result ADD CONSTRAINT fk_anomaly_detection_result_rule FOREIGN KEY (rule_id) REFERENCES anomaly_detection_rule(id);
   ALTER TABLE anomaly_detection_result ADD CONSTRAINT fk_anomaly_detection_result_pipeline_execution FOREIGN KEY (pipeline_execution_id) REFERENCES pipeline_execution(id);

Check Constraints
~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Pipeline check constraints
   ALTER TABLE pipeline ADD CONSTRAINT ck_pipeline_freshness_number CHECK (freshness_number > 0);
   ALTER TABLE pipeline ADD CONSTRAINT ck_pipeline_freshness_datepart CHECK (freshness_datepart IN ('hour', 'day', 'week', 'month', 'quarter', 'year'));
   ALTER TABLE pipeline ADD CONSTRAINT ck_pipeline_timeliness_number CHECK (timeliness_number > 0);
   ALTER TABLE pipeline ADD CONSTRAINT ck_pipeline_timeliness_datepart CHECK (timeliness_datepart IN ('hour', 'day', 'week', 'month', 'quarter', 'year'));
   
   -- Pipeline execution check constraints
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_total_rows CHECK (total_rows >= 0);
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_inserts CHECK (inserts >= 0);
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_updates CHECK (updates >= 0);
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_soft_deletes CHECK (soft_deletes >= 0);
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_duration_seconds CHECK (duration_seconds >= 0);
   ALTER TABLE pipeline_execution ADD CONSTRAINT ck_pipeline_execution_throughput CHECK (throughput >= 0);
   
   -- Anomaly detection check constraints
   ALTER TABLE anomaly_detection_rule ADD CONSTRAINT ck_anomaly_detection_rule_metric_field CHECK (metric_field IN ('total_rows', 'duration_seconds', 'throughput', 'inserts', 'updates', 'soft_deletes'));
   ALTER TABLE anomaly_detection_rule ADD CONSTRAINT ck_anomaly_detection_rule_z_threshold CHECK (z_threshold > 0);
   ALTER TABLE anomaly_detection_rule ADD CONSTRAINT ck_anomaly_detection_rule_minimum_executions CHECK (minimum_executions >= 2);
   
   -- Monitoring check constraints
   ALTER TABLE timeliness_pipeline_execution_log ADD CONSTRAINT ck_timeliness_pipeline_execution_log_duration_seconds CHECK (duration_seconds >= 0);
   ALTER TABLE timeliness_pipeline_execution_log ADD CONSTRAINT ck_timeliness_pipeline_execution_log_threshold_seconds CHECK (threshold_seconds >= 0);
   ALTER TABLE freshness_pipeline_log ADD CONSTRAINT ck_freshness_pipeline_log_threshold_hours CHECK (threshold_hours > 0);

Unique Constraints
~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   -- Unique constraints
   ALTER TABLE pipeline_type ADD CONSTRAINT uk_pipeline_type_name_group UNIQUE (name, group_name);
   ALTER TABLE address_type ADD CONSTRAINT uk_address_type_name_group UNIQUE (name, group_name);
   ALTER TABLE address ADD CONSTRAINT uk_address_name_type UNIQUE (name, address_type_id);
   ALTER TABLE address_lineage ADD CONSTRAINT uk_address_lineage_pipeline_source_target UNIQUE (pipeline_id, source_address_id, target_address_id);

Data Types
----------

Standard Types
~~~~~~~~~~~~~~

- **SERIAL**: Auto-incrementing integer primary keys
- **VARCHAR**: Variable-length character strings
- **BOOLEAN**: True/false values
- **TIMESTAMP WITH TIME ZONE**: Timezone-aware timestamps
- **DECIMAL**: Fixed-point decimal numbers
- **INTEGER**: 32-bit signed integers
- **BIGINT**: 64-bit signed integers

JSON Types
~~~~~~~~~~

- **JSONB**: Binary JSON for efficient storage and querying
- **JSON**: Text-based JSON for simple storage

Special Types
~~~~~~~~~~~~~

- **DatePartEnum**: Enumeration for date parts (hour, day, week, month, quarter, year)
- **AnomalyMetricFieldEnum**: Enumeration for anomaly detection metrics

Data Relationships
-------------------

Hierarchical Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline Execution Hierarchy**:
- Parent-child relationships via `parent_id`
- Closure table for efficient ancestor/descendant queries
- Depth tracking for relationship levels

**Address Lineage Hierarchy**:
- Source-target relationships via `source_address_id` and `target_address_id`
- Closure table for transitive relationships
- Depth tracking for lineage levels

Many-to-Many Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pipeline-Address Relationships**:
- Pipelines can have multiple addresses
- Addresses can be used by multiple pipelines
- Junction table: `address_lineage`

**Pipeline-Execution Relationships**:
- Pipelines can have multiple executions
- Executions belong to one pipeline
- Foreign key: `pipeline_id`

Data Integrity
--------------

Referential Integrity
~~~~~~~~~~~~~~~~~~~~~~

- All foreign keys have corresponding primary keys
- Cascade deletes for dependent records
- Restrict deletes for referenced records

Data Validation
~~~~~~~~~~~~~~~

- Check constraints for value ranges
- Unique constraints for business rules
- Not null constraints for required fields

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

- Indexes on frequently queried columns
- Composite indexes for multi-column queries
- Partial indexes for filtered queries
- Covering indexes for query optimization

Schema Evolution
----------------

Migration Strategy
~~~~~~~~~~~~~~~~~~

- **Alembic**: Database migration management
- **Version Control**: Track schema changes
- **Rollback Support**: Revert schema changes
- **Data Preservation**: Maintain data integrity

Migration Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

- **Backup First**: Always backup before migrations
- **Test Migrations**: Test in development first
- **Incremental Changes**: Small, focused migrations
- **Documentation**: Document schema changes

Schema Maintenance
~~~~~~~~~~~~~~~~~~

- **Regular Cleanup**: Remove unused tables/columns
- **Index Optimization**: Monitor and optimize indexes
- **Statistics Updates**: Keep statistics current
- **Performance Monitoring**: Track query performance

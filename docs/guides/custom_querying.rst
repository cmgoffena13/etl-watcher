Custom Database Querying
========================

While Watcher provides comprehensive REST APIs for most operations, there are times when you need to query the database directly for investigative, reporting, or analytical purposes. This guide covers best practices and patterns for direct database access.

.. note::
   Be cautious when querying the ``pipeline_execution`` table as it will be the main target for DML operations. 
   Use the provided index patterns to optimize your queries and avoid performance issues.

Index Utilization Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~

Watcher includes optimized indexes for common query patterns. Use these patterns to ensure efficient database access:

Date-Based Queries
-----------------

For queries filtering by ``date_recorded`` and ``pipeline_id``, use the ``ix_pipeline_execution_date_recorded_pipeline_id`` index:

.. code-block:: sql

   WITH CTE AS (
       SELECT
       id
       FROM pipeline_execution
       WHERE pipeline_id = 1
           AND date_recorded >= CURRENT_DATE - INTERVAL '7 days'
           AND date_recorded < CURRENT_DATE  /* Stay away from current records being inserted/updated */
   )
   SELECT
   pe.*  /* Columns you want to see */
   FROM pipeline_execution AS pe
   INNER JOIN CTE
       ON CTE.id = pe.id

Time-Based Queries
-----------------

For queries filtering by ``start_date``, use the ``ix_pipeline_execution_start_date`` index:

.. code-block:: sql

   WITH CTE AS (
       SELECT
       id
       FROM pipeline_execution
       WHERE start_date >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
   )
   SELECT
   pe.*  /* Columns you want to see */
   FROM pipeline_execution pe
   INNER JOIN CTE
       ON CTE.id = pe.id

Common Query Patterns
~~~~~~~~~~~~~~~~~~~~~

Pipeline Execution Analysis
--------------------------

Get recent executions for a specific pipeline:

.. code-block:: sql

   SELECT 
       pe.id,
       pe.pipeline_id,
       pe.start_date,
       pe.end_date,
       pe.duration_seconds,
       pe.total_rows,
       pe.completed_successfully,
       p.name as pipeline_name
   FROM pipeline_execution pe
   JOIN pipeline p ON pe.pipeline_id = p.id
   WHERE pe.pipeline_id = 1
       AND pe.start_date >= CURRENT_DATE - INTERVAL '7 days'
   ORDER BY pe.start_date DESC;

Anomaly Detection Analysis
-------------------------

Query anomaly detection results for a specific pipeline:

.. code-block:: sql

   SELECT 
       pe.id as execution_id,
       p.name as pipeline_name,
       adr.metric_field,
       adr.violation_value,
       adr.z_score,
       adr.historical_mean,
       adr.std_deviation_value,
       adr.detected_at
   FROM anomaly_detection_result adr
   JOIN pipeline_execution pe ON adr.pipeline_execution_id = pe.id
   JOIN pipeline p ON pe.pipeline_id = p.id
   WHERE p.id = 1  -- Filter to specific pipeline
       AND adr.detected_at >= CURRENT_DATE - INTERVAL '7 days'
   ORDER BY adr.detected_at DESC;

Lineage Analysis
----------------

Analyze data lineage relationships for a specific pipeline:

.. code-block:: sql

   SELECT 
       al.pipeline_id,
       p.name as pipeline_name,
       sa.name as source_address,
       ta.name as target_address,
       sat.name as source_type,
       tat.name as target_type
   FROM address_lineage al
   JOIN pipeline p ON al.pipeline_id = p.id
   JOIN address sa ON al.source_address_id = sa.id
   JOIN address ta ON al.target_address_id = ta.id
   JOIN address_type sat ON sa.address_type_id = sat.id
   JOIN address_type tat ON ta.address_type_id = tat.id
   WHERE p.id = 1  -- Filter to specific pipeline
   ORDER BY p.name, sa.name;

Hierarchical Execution Analysis
------------------------------

Query nested pipeline executions using the closure table:

.. code-block:: sql

   -- Get all direct children of an execution
   SELECT pe.* 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.child_execution_id
   WHERE pec.parent_execution_id = 123 
       AND pec.depth = 1;

   -- Get all downstream dependencies of an execution
   SELECT pe.* 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.child_execution_id
   WHERE pec.parent_execution_id = 123 
       AND pec.depth > 0;

   -- Get execution family tree (root + all descendants)
   SELECT pe.*, pec.depth as level 
   FROM pipeline_execution pe
   JOIN pipeline_execution_closure pec 
       ON pe.id = pec.child_execution_id
   WHERE pec.parent_execution_id = (
       -- Get root execution ID
       SELECT pec2.parent_execution_id 
       FROM pipeline_execution_closure pec2
       WHERE pec2.child_execution_id = 456
       ORDER BY pec2.depth DESC LIMIT 1
   )
   ORDER BY pec.depth, pe.id;

Best Practices
~~~~~~~~~~~~~~

Performance Considerations
--------------------------

1. **Use Indexes**: Always use the provided index patterns for optimal performance
2. **Avoid Current Records**: Stay away from records being actively inserted/updated
3. **Use CTEs**: Common Table Expressions help with complex queries and index utilization
4. **Limit Results**: Use LIMIT clauses for large result sets
5. **Monitor Query Performance**: Use EXPLAIN ANALYZE to understand query execution

Query Optimization
------------------

1. **Filter Early**: Apply WHERE clauses as early as possible
2. **Use Appropriate Joins**: INNER JOIN for required relationships, LEFT JOIN for optional ones
3. **Aggregate Efficiently**: Use GROUP BY with appropriate indexes
4. **Avoid SELECT \***: Specify only the columns you need

Safety Guidelines
-----------------

1. **Read-Only Operations**: Avoid modifying data directly in production
2. **Test Queries**: Test complex queries on development/staging first
3. **Monitor Impact**: Watch for long-running queries that might impact performance
4. **Use Transactions**: Wrap complex operations in transactions when needed

Common Use Cases
~~~~~~~~~~~~~~~~

Reporting and Analytics
-----------------------

- **Pipeline Performance**: Track execution times, success rates, and throughput
- **Data Volume Analysis**: Monitor data processing volumes over time
- **Error Analysis**: Identify patterns in failed executions
- **Resource Utilization**: Analyze pipeline resource consumption

Operational Monitoring
----------------------

- **System Health**: Monitor overall system performance
- **Capacity Planning**: Analyze growth trends and resource needs
- **Troubleshooting**: Investigate specific issues or anomalies
- **Audit Trails**: Track changes and system usage

Data Quality Analysis
---------------------

- **Anomaly Patterns**: Identify recurring anomaly types
- **Data Freshness**: Monitor data staleness across pipelines
- **Lineage Impact**: Analyze the impact of upstream changes
- **Compliance Reporting**: Generate reports for regulatory requirements

Advanced Patterns
~~~~~~~~~~~~~~~~~

Comparative Analysis
--------------------

Compare pipeline performance across different time periods for a specific pipeline:

.. code-block:: sql

   SELECT 
       p.name as pipeline_name,
       -- Current week
       COUNT(CASE WHEN pe.start_date >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as current_week_executions,
       AVG(CASE WHEN pe.start_date >= CURRENT_DATE - INTERVAL '7 days' THEN pe.duration_seconds END) as current_week_avg_duration,
       -- Previous week
       COUNT(CASE WHEN pe.start_date BETWEEN CURRENT_DATE - INTERVAL '14 days' AND CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as previous_week_executions,
       AVG(CASE WHEN pe.start_date BETWEEN CURRENT_DATE - INTERVAL '14 days' AND CURRENT_DATE - INTERVAL '7 days' THEN pe.duration_seconds END) as previous_week_avg_duration
   FROM pipeline_execution pe
   JOIN pipeline p ON pe.pipeline_id = p.id
   WHERE p.id = 1  -- Filter to specific pipeline
       AND pe.start_date >= CURRENT_DATE - INTERVAL '14 days'
   GROUP BY p.id, p.name
   ORDER BY p.name;

This guide provides the foundation for effective database querying while maintaining system performance and data integrity.

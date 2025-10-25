--DROP MATERIALIZED VIEW IF EXISTS lineage_graph_report;
CREATE MATERIALIZED VIEW IF NOT EXISTS lineage_graph_report AS
SELECT 
    alc.source_address_id,
    alc.target_address_id,
    alc.depth,
    alc.lineage_path,
    
    -- Source address details (for node details)
    sa.name as source_address_name,
    sat.name as source_address_type_name,
    sat.group_name as source_address_group_name,
    sa.address_metadata as source_address_metadata,
    
    -- Target address details (for node details)
    ta.name as target_address_name,
    tat.name as target_address_type_name,
    tat.group_name as target_address_group_name,
    ta.address_metadata as target_address_metadata,
    
    -- Pipeline details (for edge details)
    p.id as pipeline_id,
    p.name as pipeline_name,
    pt.name as pipeline_type_name,
    p.pipeline_metadata,
    p.active as pipeline_active
FROM address_lineage_closure alc
INNER JOIN address sa 
    ON alc.source_address_id = sa.id
INNER JOIN address_type sat 
    ON sa.address_type_id = sat.id
INNER JOIN address ta 
    ON alc.target_address_id = ta.id  
INNER JOIN address_type tat 
    ON ta.address_type_id = tat.id
LEFT JOIN address_lineage al 
    ON alc.source_address_id = al.source_address_id 
    AND alc.target_address_id = al.target_address_id
LEFT JOIN pipeline p 
    ON al.pipeline_id = p.id
LEFT JOIN pipeline_type pt 
    ON p.pipeline_type_id = pt.id
WHERE alc.depth > 0;

CREATE INDEX IF NOT EXISTS ix_lineage_graph_report_lineage_path_filtered
    ON lineage_graph_report USING GIN (lineage_path) WHERE depth = 1;
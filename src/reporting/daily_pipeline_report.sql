--DROP MATERIALIZED VIEW IF EXISTS daily_pipeline_report;
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_pipeline_report AS
with CTE as (
	select
	id
	from pipeline_execution
	where date_recorded >= CURRENT_DATE - INTERVAL '30 days'
		and date_recorded < CURRENT_DATE
)
select
	pe.date_recorded,
	pt.name as pipeline_type_name,
	p.name as pipeline_name,
	COUNT(*) as total_executions,
	SUM(CASE WHEN pe.completed_successfully = false THEN 1 ELSE 0 END) as failed_executions,
	    ROUND(
	        (SUM(CASE WHEN pe.completed_successfully = false THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 
	        2
	    ) as error_percentage,
    SUM(COALESCE(pe.inserts, 0)) as daily_inserts,
    SUM(COALESCE(pe.updates, 0)) as daily_updates,
    SUM(COALESCE(pe.soft_deletes, 0)) as daily_soft_deletes,
    SUM(COALESCE(pe.total_rows, 0)) as daily_total_rows,
    ROUND(AVG(COALESCE(pe.duration_seconds, 0)), 2) as avg_duration_seconds,
	ROUND(
	    SUM(pe.total_rows::DECIMAL) / NULLIF(SUM(pe.duration_seconds::DECIMAL), 0), 
	    4
	) as daily_throughput
from pipeline_execution pe 
inner join CTE
	on CTE.id = PE.id
inner join pipeline p
	on p.id = pe.pipeline_id 
inner join pipeline_type pt
	on pt.id = p.pipeline_type_id
group by
pe.date_recorded, pt.name, p.name;

CREATE INDEX IF NOT EXISTS ix_daily_pipeline_report_date_recorded 
	ON daily_pipeline_report(date_recorded, pipeline_name, pipeline_type_name);
CREATE INDEX IF NOT EXISTS ix_daily_pipeline_report_pipeline_type_name 
	ON daily_pipeline_report(date_recorded, pipeline_type_name, pipeline_name);
import logging
import uuid

import pendulum
from sqlalchemy import text
from sqlmodel import Session

from src.notifier import AlertLevel, send_slack_message

logger = logging.getLogger(__name__)


async def db_check_pipeline_freshness(session: Session):
    timestamp = pendulum.now("UTC")

    # Use unique temp table name to prevent conflicts with concurrent requests
    temp_table_name = f"check_pipeline_freshness_temp_{uuid.uuid4().hex[:8]}"

    await session.exec(text(f"DROP TABLE IF EXISTS {temp_table_name}"))

    pipelines_query = text(f"""
        WITH CTE AS (
            SELECT
                cte_p.id as pipeline_id,
                cte_pt.freshness_number,
                cte_pt.freshness_datepart
            FROM pipeline_type AS cte_pt
            INNER JOIN pipeline AS cte_p
                ON cte_p.pipeline_type_id = cte_pt.id
            WHERE cte_pt.mute_freshness_check = false
        )
        SELECT
            p.id as pipeline_id,
            p.name as pipeline_name,
            p.last_target_insert,
            p.last_target_update,
            p.last_target_soft_delete,
            p.freshness_number as child_freshness_number,
            p.freshness_datepart as child_freshness_datepart,
            pt.freshness_number as parent_freshness_number,
            pt.freshness_datepart as parent_freshness_datepart
        INTO TEMP TABLE {temp_table_name}
        FROM pipeline AS p
        INNER JOIN CTE AS pt
            ON pt.pipeline_id = p.id
        WHERE p.mute_freshness_check = false
    """)
    await session.exec(pipelines_query)

    pipelines_query = text(f"""
        SELECT
            pipeline_id,
            pipeline_name,
            last_target_insert,
            last_target_update,
            last_target_soft_delete,
            child_freshness_number,
            child_freshness_datepart,
            parent_freshness_number,
            parent_freshness_datepart
        FROM {temp_table_name}
    """)

    pipelines = (await session.exec(pipelines_query)).fetchall()

    logger.info(f"Processing {len(pipelines)} pipelines for freshness check")

    fail_results = []
    for pipeline in pipelines:
        (
            pipeline_id,
            pipeline_name,
            last_insert,
            last_update,
            last_delete,
            child_number,
            child_datepart,
            parent_number,
            parent_datepart,
        ) = pipeline

        max_dml = None
        for ts in [last_insert, last_update, last_delete]:
            if ts is not None:
                if max_dml is None or ts > max_dml:
                    max_dml = ts

        if max_dml is None:
            continue

        if child_datepart and child_number:
            freshness_datepart = child_datepart
            freshness_number = child_number
            used_child_config = True
        elif parent_datepart and parent_number:
            freshness_datepart = parent_datepart
            freshness_number = parent_number
            used_child_config = False
        else:
            logger.warning(
                f"Pipeline {pipeline_id} ({pipeline_name}) skipped - incomplete freshness settings "
                f"(child: {child_datepart}, {child_number}; parent: {parent_datepart}, {parent_number})"
            )
            continue

        # Calculate threshold time
        calculated_time = _calculate_timely_time(
            max_dml, freshness_datepart, freshness_number
        )

        if calculated_time < timestamp:
            fail_results.append(
                {
                    "pipeline_id": pipeline_id,
                    "pipeline_name": pipeline_name,
                    "last_dml": max_dml,
                    "freshness_number": freshness_number,
                    "freshness_datepart": freshness_datepart,
                    "used_child_config": used_child_config,
                }
            )

            logger.warning(
                f"Pipeline {pipeline_id} ({pipeline_name}) failed freshness check"
            )

    if fail_results:
        logger.warning(
            f"Pipeline Freshness Check Failed - {len(fail_results)} pipeline(s) overdue"
        )
        await session.exec(text(f"DROP TABLE IF EXISTS {temp_table_name}"))

        # Check for PostgreSQL parameter limit (65,535)
        # Each fail_result generates 6 values in the VALUES clause
        total_values = len(fail_results) * 6
        if total_values > 65000:
            logger.error(
                f"Too many values ({total_values}) - exceeds PostgreSQL parameter limit of 65,535"
            )

        values_clauses = []
        for result in fail_results:
            values_clauses.append(
                f"({result['pipeline_id']}, '{result['last_dml']}'::timestamp with time zone, '{timestamp}'::timestamp with time zone, {result['freshness_number']}, '{result['freshness_datepart']}'::datepartenum, {result.get('used_child_config', False)})"
            )

        values_sql = ",\n".join(values_clauses)
        insert_query = text(f"""
            INSERT INTO freshness_pipeline_log (pipeline_id, last_dml_timestamp, evaluation_timestamp, freshness_number, freshness_datepart, used_child_config)
            SELECT 
            v.pipeline_id, 
            v.last_dml_timestamp, 
            v.evaluation_timestamp, 
            v.freshness_number, 
            v.freshness_datepart, 
            v.used_child_config 
            FROM (VALUES {values_sql}) AS v(pipeline_id, last_dml_timestamp, evaluation_timestamp, freshness_number, freshness_datepart, used_child_config)
            WHERE NOT EXISTS (
                SELECT 1 
                FROM freshness_pipeline_log f
                WHERE f.pipeline_id = v.pipeline_id 
                    AND f.last_dml_timestamp = v.last_dml_timestamp
            )
        """)

        result = await session.exec(insert_query)
        rows_inserted = result.rowcount
        await session.commit()
        values_clauses.clear()

        logger.info(f"Inserted {rows_inserted} new freshness pipeline log records")

        try:
            pipeline_details = []
            for result in fail_results:
                pipeline_details.append(
                    f"\t• {result['pipeline_name']} (ID: {result['pipeline_id']}): "
                    f"Last DML {result['last_dml']}, Expected within {
                        result['freshness_number']
                    } {
                        _get_display_datepart(
                            result['freshness_datepart'], result['freshness_number']
                        )
                    }"
                )
            send_slack_message(
                level=AlertLevel.WARNING,
                title="Freshness Check - Pipeline DML",
                message=f"Pipeline Freshness Check Failed - {len(fail_results)} pipeline(s) overdue",
                details={
                    "Failed Pipelines": "\n" + "\n".join(pipeline_details),
                    "Total Overdue": len(fail_results),
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to send Slack notification for freshness failures: {e}"
            )
        return {"status": "warning"}
    else:
        logger.info("All pipelines passed freshness check")
        await session.exec(text(f"DROP TABLE IF EXISTS {temp_table_name}"))

    return {"status": "success"}


def _calculate_timely_time(max_dml, datepart, number):
    """Calculate the expected time based on datepart and number"""
    # Convert to pendulum if it's a regular datetime
    if hasattr(max_dml, "add"):
        dml_time = max_dml
    else:
        dml_time = pendulum.instance(max_dml)

    if datepart.upper() == "MINUTE":
        return dml_time.add(minutes=number)
    elif datepart.upper() == "HOUR":
        return dml_time.add(hours=number)
    elif datepart.upper() == "DAY":
        return dml_time.add(days=number)
    elif datepart.upper() == "WEEK":
        return dml_time.add(weeks=number)
    elif datepart.upper() == "MONTH":
        return dml_time.add(months=number)
    elif datepart.upper() == "YEAR":
        return dml_time.add(years=number)
    else:
        raise ValueError(f"Unsupported datepart: {datepart}")


def _get_display_datepart(datepart, number):
    """Convert datepart to display format (singular/plural)"""
    datepart_lower = datepart.lower()
    if number == 1:
        return datepart_lower
    else:
        return f"{datepart_lower}s"

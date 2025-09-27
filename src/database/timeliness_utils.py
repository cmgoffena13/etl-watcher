import logging
import uuid

import pendulum
from fastapi import Response
from sqlalchemy import text
from sqlmodel import Session

from src.database.db import _calculate_timely_time, _get_display_datepart
from src.notifier import AlertLevel, send_slack_message

logger = logging.getLogger(__name__)


async def db_check_pipeline_execution_timeliness(
    session: Session, response: Response, lookback_minutes: int
):
    logger.info("Starting Pipeline Execution Timeliness Check")
    lookback_timestamp = pendulum.now("UTC").subtract(minutes=lookback_minutes)

    # Use unique temp table name to prevent conflicts with concurrent requests
    temp_table_name = f"timeliness_pipeline_execution_log_temp_{uuid.uuid4().hex[:8]}"

    await session.exec(text(f"DROP TABLE IF EXISTS {temp_table_name}"))

    cte_query = text(f"""
        WITH CTE AS (
            SELECT id
            FROM pipeline_execution
            WHERE start_date > :lookback_timestamp
        )
        SELECT
            pe.id,
            pe.pipeline_id,
            pe.duration_seconds,
            pe.start_date,
            pe.end_date,
            pe.completed_successfully
        INTO TEMP TABLE {temp_table_name}
        FROM pipeline_execution AS pe
        INNER JOIN CTE
            ON CTE.id = pe.id
    """)

    await session.exec(
        cte_query,
        params={
            "lookback_timestamp": lookback_timestamp,
        },
    )

    results_query = text(f"""
        SELECT
            t.id,
            t.pipeline_id,
            t.duration_seconds,
            t.start_date,
            t.end_date,
            t.completed_successfully,
            p.timeliness_number AS child_timely_number,
            p.timeliness_datepart AS child_timely_datepart,
            pt.timeliness_number AS parent_timely_number,
            pt.timeliness_datepart AS parent_timely_datepart
        FROM {temp_table_name} AS t
        INNER JOIN pipeline AS p
            ON p.id = t.pipeline_id 
            AND p.mute_timeliness_check = FALSE
        INNER JOIN pipeline_type AS pt
            ON pt.id = p.pipeline_type_id 
            AND pt.mute_timeliness_check = FALSE
    """)
    executions_list = (await session.exec(results_query)).all()
    await session.exec(text(f"DROP TABLE IF EXISTS {temp_table_name}"))
    now_time = pendulum.now("UTC")

    fail_results = []
    for execution in executions_list:
        (
            id,
            pipeline_id,
            duration_seconds,
            start_date,
            end_date,
            completed_successfully,
            child_number,
            child_datepart,
            parent_number,
            parent_datepart,
        ) = execution
        if child_datepart and child_number:
            timely_datepart = child_datepart
            timely_number = child_number
            used_child_config = True
        elif parent_datepart and parent_number:
            timely_datepart = parent_datepart
            timely_number = parent_number
            used_child_config = False
        else:
            logger.warning(
                f"Execution {id} skipped - incomplete timely settings"
                f"(child: {child_datepart}, {child_number}; parent: {parent_datepart}, {parent_number})"
            )
            continue

        execution_threshold = _calculate_timely_time(
            start_date, timely_datepart, timely_number
        )

        # Check if lookback period is shorter than execution threshold
        execution_threshold_duration_minutes = int(
            (execution_threshold - start_date).total_seconds() / 60
        )
        if lookback_minutes < execution_threshold_duration_minutes:
            config_source = "child" if used_child_config else "parent"
            logger.warning(
                f"Pipeline {pipeline_id} execution threshold ({execution_threshold_duration_minutes} minutes, {config_source} config) "
                f"exceeds lookback period ({lookback_minutes} minutes). "
                f"Overdue executions may not be detected."
            )

        is_overdue = False
        if completed_successfully is None:
            # Running pipeline
            if now_time > execution_threshold:
                is_overdue = True
                execution_status = "running"
                actual_duration = int((now_time - start_date).total_seconds())
        elif completed_successfully:
            # Completed pipeline
            if end_date > execution_threshold:
                is_overdue = True
                execution_status = "completed"
                actual_duration = duration_seconds
        else:
            continue

        if is_overdue:
            fail_results.append(
                {
                    "pipeline_execution_id": id,
                    "pipeline_id": pipeline_id,
                    "duration_seconds": actual_duration,
                    "seconds_threshold": int(
                        (execution_threshold - start_date).total_seconds()
                    ),
                    "timely_number": timely_number,
                    "timely_datepart": timely_datepart,
                    "used_child_config": used_child_config,
                    "execution_status": execution_status,
                }
            )
    executions_list.clear()

    if fail_results:
        logger.warning(
            f"Pipeline Execution Timeliness Check Failed - {len(fail_results)} execution(s) overdue"
        )

        # Check for PostgreSQL parameter limit (65,535)
        # Each fail_result generates 7 values in the VALUES clause
        total_values = len(fail_results) * 7
        if total_values > 65000:
            logger.error(
                f"Too many values ({total_values}) - exceeds PostgreSQL parameter limit of 65,535"
            )

        values_sql = ",\n".join(
            f"({result['pipeline_execution_id']}, {result['pipeline_id']}, {result['duration_seconds']}, {result['seconds_threshold']}, '{result['execution_status']}', {result['timely_number']}, '{result['timely_datepart']}'::datepartenum, {result['used_child_config']})"
            for result in fail_results
        )
        insert_query = text(f"""
            INSERT INTO timeliness_pipeline_execution_log (pipeline_execution_id, pipeline_id, duration_seconds, seconds_threshold, execution_status, timely_number, timely_datepart, used_child_config)
            SELECT 
            v.pipeline_execution_id, 
            v.pipeline_id, 
            v.duration_seconds, 
            v.seconds_threshold,
            v.execution_status,
            v.timely_number,
            v.timely_datepart,
            v.used_child_config
            FROM (VALUES {values_sql}) AS v(pipeline_execution_id, pipeline_id, duration_seconds, seconds_threshold, execution_status, timely_number, timely_datepart, used_child_config)
            WHERE NOT EXISTS (
                SELECT 1 
                FROM timeliness_pipeline_execution_log t
                WHERE t.pipeline_execution_id = v.pipeline_execution_id
            )
            RETURNING pipeline_execution_id
        """)

        result = await session.exec(insert_query)
        inserted_records = result.fetchall()
        rows_inserted = result.rowcount
        await session.commit()

        logger.info(
            f"Inserted {rows_inserted} new timeliness pipeline execution log records"
        )

        if rows_inserted > 0:
            try:
                inserted_execution_ids = {record[0] for record in inserted_records}

                new_fail_results = [
                    result
                    for result in fail_results
                    if result["pipeline_execution_id"] in inserted_execution_ids
                ]

                if new_fail_results:
                    pipeline_details = "\n".join(
                        f"\t• Pipeline Execution ID: {result['pipeline_execution_id']} (Pipeline ID: {result['pipeline_id']}): "
                        f"{result['duration_seconds']} seconds ({result['execution_status']}), Expected within {result['timely_number']} {_get_display_datepart(result['timely_datepart'], result['timely_number'])} "
                        f"({'child' if result['used_child_config'] else 'parent'} config)"
                        for result in new_fail_results
                    )

                    await send_slack_message(
                        level=AlertLevel.WARNING,
                        title="Timeliness Check - Pipeline Execution",
                        message=f"Pipeline Execution Timeliness Check Failed - {len(new_fail_results)} NEW execution(s) overdue",
                        details={"Failed Executions": "\n" + pipeline_details},
                    )
            except Exception as e:
                logger.error(
                    f"Failed to send Slack notification for timeliness executions: {e}"
                )
        else:
            logger.info(
                "No new timeliness failures to report - all failures were already logged"
            )

        return {"status": "warning"}
    else:
        logger.info("All pipeline executions are within timely thresholds")
        return {"status": "success"}

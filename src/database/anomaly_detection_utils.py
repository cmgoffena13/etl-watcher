import logging
import statistics
from typing import Optional

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import delete, func, select, update
from sqlmodel import Session

from src.database.models.anomaly_detection import (
    AnomalyDetectionResult,
    AnomalyDetectionRule,
)
from src.database.models.pipeline import Pipeline
from src.database.models.pipeline_execution import PipelineExecution
from src.models.anomaly_detection import (
    AnomalyDetectionRulePatchInput,
    AnomalyDetectionRulePostInput,
    AnomalyDetectionRulePostOutput,
    UnflagAnomalyInput,
)
from src.notifier import AlertLevel, send_slack_message
from src.types import AnomalyMetricFieldEnum

logger = logging.getLogger(__name__)


async def db_get_or_create_anomaly_detection_rule(
    session: Session, rule: AnomalyDetectionRulePostInput, response: Response
) -> AnomalyDetectionRulePostOutput:
    created = False

    rule_id = (
        await session.exec(
            select(AnomalyDetectionRule.id)
            .where(AnomalyDetectionRule.pipeline_id == rule.pipeline_id)
            .where(AnomalyDetectionRule.metric_field == rule.metric_field)
        )
    ).scalar_one_or_none()

    if rule_id is None:
        logger.info(
            f"Anomaly Detection Rule: {rule.metric_field.value} for pipeline {rule.pipeline_id} Not Found. Creating..."
        )
        new_rule = AnomalyDetectionRule(**rule.model_dump(exclude_unset=True))

        stmt = (
            AnomalyDetectionRule.__table__.insert()
            .returning(AnomalyDetectionRule.id)
            .values(**new_rule.model_dump(exclude={"id"}))
        )
        rule_id = (await session.exec(stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(
            f"Anomaly Detection Rule: {rule.metric_field.value} for pipeline {rule.pipeline_id} Successfully Created"
        )

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return {"id": rule_id}


async def db_update_anomaly_detection_rule(
    session: Session, patch: AnomalyDetectionRulePatchInput
) -> AnomalyDetectionRule:
    rule = (
        await session.exec(
            select(AnomalyDetectionRule).where(AnomalyDetectionRule.id == patch.id)
        )
    ).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Anomaly detection rule not found")

    update_data = patch.model_dump(exclude_unset=True, exclude={"id"})
    for field, value in update_data.items():
        setattr(rule, field, value)

    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


async def db_unflag_anomaly(session: Session, input: UnflagAnomalyInput):
    pipeline_execution = await session.get(
        PipelineExecution, input.pipeline_execution_id
    )
    if not pipeline_execution:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline execution {input.pipeline_execution_id} not found",
        )
    if not pipeline_execution.anomaly_flags:
        raise HTTPException(
            status_code=404,
            detail=f"No anomaly flags found for execution {input.pipeline_execution_id}",
        )

    # Check which requested metrics are actually flagged (true)
    requested_metrics = [metric.value for metric in input.metric_field]
    actually_flagged_metrics = [
        metric
        for metric in requested_metrics
        if metric in pipeline_execution.anomaly_flags
        and pipeline_execution.anomaly_flags.get(metric, False) is True
    ]

    if not actually_flagged_metrics:
        raise HTTPException(
            status_code=404,
            detail=f"None of the requested metrics {requested_metrics} are currently flagged",
        )

    # Get rule IDs for the metrics that are actually flagged as True
    actually_flagged_metric_enums = [
        AnomalyMetricFieldEnum(metric) for metric in actually_flagged_metrics
    ]
    rule_ids = (
        (
            await session.exec(
                select(AnomalyDetectionRule.id).where(
                    AnomalyDetectionRule.pipeline_id == input.pipeline_id,
                    AnomalyDetectionRule.metric_field.in_(
                        actually_flagged_metric_enums
                    ),
                )
            )
        )
        .scalars()
        .all()
    )

    # Update flags
    anomaly_flags_new = pipeline_execution.anomaly_flags.copy()
    for metric in actually_flagged_metrics:
        anomaly_flags_new[metric] = False

    savepoint = await session.begin_nested()
    try:
        # Delete anomaly results
        await session.exec(
            delete(AnomalyDetectionResult).where(
                AnomalyDetectionResult.pipeline_execution_id
                == input.pipeline_execution_id,
                AnomalyDetectionResult.rule_id.in_(rule_ids),
            )
        )

        # Update flags
        await session.exec(
            update(PipelineExecution)
            .where(PipelineExecution.id == input.pipeline_execution_id)
            .values(anomaly_flags=anomaly_flags_new)
        )

        await savepoint.commit()
        await session.commit()

    except Exception as e:
        await savepoint.rollback()
        raise

    logger.info(
        f"Unflagged anomalies for pipeline execution {input.pipeline_execution_id}"
    )


async def db_detect_anomalies_for_pipeline_execution(
    session: Session, pipeline_id: int, pipeline_execution_id: int
):
    logger.info(
        f"Detecting anomalies for pipeline {pipeline_id} for execution {pipeline_execution_id}"
    )

    # First query: Get rule IDs using index
    rule_ids_query = select(AnomalyDetectionRule.id).where(
        AnomalyDetectionRule.pipeline_id == pipeline_id,
        AnomalyDetectionRule.active == True,
    )
    rule_ids = (await session.exec(rule_ids_query)).scalars().all()

    if not rule_ids:
        logger.info(f"No active rules found for pipeline {pipeline_id}")
        return

    # Second query: PK seeks for full rule data
    rules_query = select(
        AnomalyDetectionRule.id,
        AnomalyDetectionRule.pipeline_id,
        AnomalyDetectionRule.lookback_days,
        AnomalyDetectionRule.minimum_executions,
        AnomalyDetectionRule.metric_field,
        AnomalyDetectionRule.z_threshold,
    ).where(AnomalyDetectionRule.id.in_(rule_ids))

    rules = (await session.exec(rules_query)).all()
    rule_ids.clear()

    max_lookback_days = max(rule.lookback_days for rule in rules)
    all_same_lookback = all(rule.lookback_days == max_lookback_days for rule in rules)
    lookback_date = pendulum.now("UTC").subtract(days=max_lookback_days)

    hour_recorded = (
        await session.exec(
            select(PipelineExecution.hour_recorded).where(
                PipelineExecution.id == pipeline_execution_id
            )
        )
    ).scalar_one()

    ids_query = (
        select(PipelineExecution.id)
        .where(PipelineExecution.pipeline_id == pipeline_id)
        .where(PipelineExecution.hour_recorded == hour_recorded)
        .where(PipelineExecution.end_date >= lookback_date)
        .where(PipelineExecution.end_date.is_not(None))
        .where(PipelineExecution.completed_successfully == True)
    )
    execution_ids = (await session.exec(ids_query)).scalars().all()

    base_columns = [PipelineExecution.id, PipelineExecution.anomaly_flags]
    if not all_same_lookback:
        base_columns.append(PipelineExecution.end_date)

    # Only bring in metric columns we actually need from pipeline execution
    for rule in rules:
        metric_field = rule.metric_field.value
        if hasattr(PipelineExecution, metric_field):
            base_columns.append(getattr(PipelineExecution, metric_field))

    # PK seek for execution data
    executions_query = select(*base_columns).where(
        PipelineExecution.id.in_(execution_ids)
    )
    all_executions = (await session.exec(executions_query)).all()

    # Collect all anomaly results and flags
    anomaly_results = []
    anomaly_flags = {}
    anomaly_metrics = []

    for rule in rules:
        try:
            anomaly_data = await _detect_anomalies_for_rule_batch(
                session,
                rule,
                all_executions,
                all_same_lookback,
                pipeline_execution_id,
            )

            if anomaly_data:
                anomaly_results.append(AnomalyDetectionResult(**anomaly_data))
                anomaly_flags[rule.metric_field.value] = True
                anomaly_metrics.append(rule.metric_field.value)

        except Exception as e:
            logger.error(
                f"Error detecting anomalies for rule '{rule.metric_field.value}' for pipeline {rule.pipeline_id} for execution {pipeline_execution_id}: {e}"
            )
            continue

    if anomaly_results:
        savepoint = await session.begin_nested()
        try:
            session.add_all(anomaly_results)

            await session.exec(
                update(PipelineExecution)
                .where(PipelineExecution.id == pipeline_execution_id)
                .values(anomaly_flags=anomaly_flags)
            )

            await savepoint.commit()
            await session.commit()

        except Exception as e:
            await savepoint.rollback()
            logger.error(f"Failed to commit anomaly detection results: {e}")
            raise

        try:
            logger.info(
                f"Anomalies detected: {', '.join(anomaly_metrics)} for pipeline {pipeline_id} for execution {pipeline_execution_id}"
            )

            await _send_anomaly_alert(
                session,
                pipeline_id,
                pipeline_execution_id,
                anomaly_results,
                anomaly_metrics,
            )
        except Exception as e:
            logger.error(f"Failed to send anomaly alert: {e}")
            raise


async def _detect_anomalies_for_rule_batch(
    session: Session,
    rule: AnomalyDetectionRule,
    executions: list,
    all_same_lookback: bool,
    current_execution_id: int,
) -> Optional[dict]:  # Return anomaly data dict or None
    logger.info(
        f"Detecting anomalies for rule '{rule.metric_field.value}' on pipeline {rule.pipeline_id} for execution {current_execution_id}"
    )
    # Filter executions by this rule's specific lookback period
    if all_same_lookback:
        rule_executions = executions
    else:
        rule_lookback_date = pendulum.now("UTC").subtract(days=rule.lookback_days)
        rule_executions = [
            exec for exec in executions if exec.end_date >= rule_lookback_date
        ]

    # Skip current execution when building baseline, so minus one
    if len(rule_executions) - 1 < rule.minimum_executions:
        logger.warning(
            f"Pipeline {rule.pipeline_id}: Not enough executions for rule '{rule.metric_field.value}': {len(rule_executions) - 1} < {rule.minimum_executions}"
        )
        return

    current_execution = None

    metric_values = []
    for execution in rule_executions:
        # Skip current execution when building baseline
        if execution.id == current_execution_id:
            current_execution = execution
            continue

        # Skip executions that have anomalies for THIS SPECIFIC METRIC
        if execution.anomaly_flags and execution.anomaly_flags.get(
            rule.metric_field.value, False
        ):
            continue  # Skip this execution for baseline calculation, will skew

        metric_value = getattr(execution, rule.metric_field.value)
        if metric_value is not None:
            # Convert throughput DECIMAL to float for statistics calculations
            if rule.metric_field.value == "throughput":
                metric_values.append(float(metric_value))
            else:
                metric_values.append(metric_value)

    # Check minimum executions AFTER filtering out anomalies and current execution
    if len(metric_values) < rule.minimum_executions:
        logger.warning(
            f"Pipeline {rule.pipeline_id}: Not enough metric values for rule '{rule.metric_field}': {len(metric_values)} < {rule.minimum_executions}"
        )
        return

    baseline_mean = statistics.mean(metric_values)
    baseline_std = statistics.stdev(metric_values) if len(metric_values) > 1 else 0
    metric_values.clear()

    # Handle case where std dev is 0 (all values are identical, like 0 rows)
    if baseline_std == 0:
        logger.warning(
            f"Pipeline {rule.pipeline_id}: No variance in data for rule '{rule.metric_field}', skipping anomaly detection"
        )
        return

    # Calculate threshold values for easy reference
    # Min threshold can't be below zero for metrics like duration, rows, etc.
    threshold_min_value = max(
        0, baseline_mean - (float(rule.z_threshold) * baseline_std)
    )
    threshold_max_value = baseline_mean + (float(rule.z_threshold) * baseline_std)

    logger.info(
        f"Pipeline {rule.pipeline_id}: Checking current execution {current_execution_id} for anomalies on rule '{rule.metric_field.value}': Threshold range: [{threshold_min_value}, {threshold_max_value}], Baseline mean: {baseline_mean}, Baseline std: {baseline_std}"
    )

    current_value = getattr(current_execution, rule.metric_field.value, None)
    if current_value is None:
        logger.info(
            f"Pipeline {rule.pipeline_id}: No metric value for rule '{rule.metric_field.value}' for current execution {current_execution_id}"
        )
        return

    # Convert current_value to float for calculations if it's throughput
    if rule.metric_field.value == "throughput":
        current_value = float(current_value)

    # Check for anomalies (both above upper bound and below lower bound)
    is_anomaly = (
        current_value > threshold_max_value or current_value < threshold_min_value
    )

    if is_anomaly:
        # Calculate z-score for context (how many standard deviations from mean)
        z_score = (current_value - baseline_mean) / baseline_std

        return {
            "pipeline_execution_id": current_execution.id,
            "rule_id": rule.id,
            "violation_value": current_value,
            "historical_mean": baseline_mean,
            "std_deviation_value": baseline_std,
            "z_threshold": float(rule.z_threshold),
            "threshold_min_value": threshold_min_value,
            "threshold_max_value": threshold_max_value,
            "z_score": z_score,
            "context": {
                "lookback_days": rule.lookback_days,
                "minimum_executions": rule.minimum_executions,
                "execution_count": len(metric_values),
            },
        }

    return None


async def _send_anomaly_alert(
    session: Session,
    pipeline_id: int,
    pipeline_execution_id: int,
    anomaly_results: list,
    anomaly_metrics: list,
):
    """Send a single alert for all anomalies detected on an execution"""
    try:
        # Get pipeline name for display
        pipeline_name_query = select(Pipeline.name).where(Pipeline.id == pipeline_id)
        pipeline_name = (await session.exec(pipeline_name_query)).scalar_one_or_none()
        pipeline_display = (
            f"'{pipeline_name}'" if pipeline_name else f"ID:{pipeline_id}"
        )

        anomaly_details = []
        for i, anomaly in enumerate(anomaly_results):
            details = f"\n\t• {anomaly_metrics[i]}: {anomaly.violation_value} (Range: {anomaly.threshold_min_value:.0f} - {anomaly.threshold_max_value:.0f})"
            anomaly_details.append(details)

        await send_slack_message(
            level=AlertLevel.WARNING,
            title="Anomaly Detection",
            message=f"Anomalies detected in Pipeline {pipeline_display} - Pipeline Execution ID {pipeline_execution_id} flagged",
            details={
                "Total Anomalies": len(anomaly_results),
                "Metrics": anomaly_metrics,
                "Anomalies": "\n".join(anomaly_details),
            },
        )
    except Exception as e:
        logger.error(
            f"Failed to send Slack notification for anomalies on pipeline '{pipeline_name}' for execution {pipeline_execution_id}: {e}"
        )

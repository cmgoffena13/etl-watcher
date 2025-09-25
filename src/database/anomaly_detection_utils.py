import logging
import statistics

import pendulum
from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlmodel import Session

from src.database.models.anomaly_detection import (
    AnomalyDetectionResult,
    AnomalyDetectionRule,
)
from src.database.models.pipeline_execution import PipelineExecution
from src.models.anomaly_detection import (
    AnomalyDetectionRulePatchInput,
    AnomalyDetectionRulePostInput,
    AnomalyDetectionRulePostOutput,
)
from src.notifier import AlertLevel, send_slack_message

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
        AnomalyDetectionRule.std_deviation_threshold_multiplier,
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

    base_columns = [PipelineExecution.id]
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

    for rule in rules:
        try:
            await _detect_anomalies_for_rule_batch(
                session,
                rule,
                all_executions,
                all_same_lookback,
                pipeline_execution_id,
            )
        except Exception as e:
            logger.error(
                f"Error detecting anomalies for rule '{rule.metric_field.value}' for pipeline {rule.pipeline_id}: {e}"
            )
            continue


async def _detect_anomalies_for_rule_batch(
    session: Session,
    rule: AnomalyDetectionRule,
    executions: list,
    all_same_lookback: bool,
    current_execution_id: int,
):
    logger.info(
        f"Detecting anomalies for rule '{rule.metric_field.value}' on pipeline {rule.pipeline_id}"
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
            f"Not enough executions for rule '{rule.metric_field.value}': {len(rule_executions) - 1} < {rule.minimum_executions}"
        )
        return

    current_execution = None

    metric_values = []
    for execution in rule_executions:
        # Skip current execution when building baseline
        if execution.id == current_execution_id:
            current_execution = execution
            continue

        metric_value = getattr(execution, rule.metric_field.value)
        if metric_value is not None:
            # Convert throughput DECIMAL to float for statistics calculations
            if rule.metric_field.value == "throughput":
                metric_values.append(float(metric_value))
            else:
                metric_values.append(metric_value)

    if len(metric_values) < rule.minimum_executions:
        logger.warning(
            f"Not enough metric values for rule '{rule.metric_field}': {len(metric_values)} < {rule.minimum_executions}"
        )
        return

    baseline_mean = statistics.mean(metric_values)
    baseline_std = statistics.stdev(metric_values) if len(metric_values) > 1 else 0
    metric_values.clear()

    # Handle case where std dev is 0 (all values are identical, like 0 rows)
    if baseline_std == 0:
        logger.warning(
            f"No variance in data for rule '{rule.metric_field}', skipping anomaly detection"
        )
        return

    # Define anomaly threshold using standard deviations
    threshold = baseline_mean + (rule.std_deviation_threshold_multiplier * baseline_std)
    logger.info(
        f"Checking current execution {current_execution_id} for anomalies on rule '{rule.metric_field.value}': Threshold: {threshold}, Baseline mean: {baseline_mean}, Baseline std: {baseline_std}"
    )

    current_value = getattr(current_execution, rule.metric_field.value, None)
    if current_value is None:
        logger.info(
            f"No metric value for rule '{rule.metric_field.value}' for current execution {current_execution_id}"
        )
        return

    # Convert current_value to float for calculations if it's throughput
    if rule.metric_field.value == "throughput":
        current_value = float(current_value)

    if current_value > threshold:
        # Calculate z-score (how many standard deviations above mean)
        z_score = (current_value - baseline_mean) / baseline_std
        deviation_percentage = ((current_value - baseline_mean) / baseline_mean) * 100

        # Confidence score based on how many std devs beyond the threshold
        confidence_score = min(1.0, z_score / rule.std_deviation_threshold_multiplier)

        anomaly_result = AnomalyDetectionResult(
            pipeline_execution_id=current_execution.id,
            rule_id=rule.id,
            violation_value=current_value,
            baseline_value=baseline_mean,
            deviation_percentage=deviation_percentage,
            confidence_score=confidence_score,
            context={
                "threshold_multiplier": rule.std_deviation_threshold_multiplier,
                "baseline_std": baseline_std,
                "lookback_days": rule.lookback_days,
                "execution_count": len(metric_values),
                "z_score": z_score,
                "threshold_value": threshold,
            },
        )

        session.add(anomaly_result)
        await session.commit()

        try:
            anomaly_details = (
                f"\n\t• value:{anomaly_result.violation_value} (baseline: {anomaly_result.baseline_value:.2f}, "
                f"deviation: {anomaly_result.deviation_percentage:.1f}%, "
                f"confidence: {anomaly_result.confidence_score:.2f})"
            )

            await send_slack_message(
                level=AlertLevel.WARNING,
                title="Anomaly Detection",
                message=f"Anomaly detected in Pipeline {rule.pipeline_id} - Pipeline Execution ID {anomaly_result.pipeline_execution_id} flagged",
                details={
                    "Metric": rule.metric_field.value,
                    "Threshold Multiplier": rule.std_deviation_threshold_multiplier,
                    "Lookback Days": rule.lookback_days,
                    "Anomaly": f"\n{anomaly_details}",
                },
            )
        except Exception as e:
            logger.error(f"Failed to send Slack notification for anomaly: {e}")

import logging
import statistics
from typing import List

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
    AnomalyDetectionResultOutput,
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
            select(AnomalyDetectionRule.id).where(
                AnomalyDetectionRule.name == rule.name
            )
        )
    ).scalar_one_or_none()

    if rule_id is None:
        logger.info(f"Anomaly Detection Rule '{rule.name}' Not Found. Creating...")
        new_rule = AnomalyDetectionRule(**rule.model_dump(exclude_unset=True))

        stmt = (
            AnomalyDetectionRule.__table__.insert()
            .returning(AnomalyDetectionRule.id)
            .values(**new_rule.model_dump(exclude={"id"}))
        )
        rule_id = (await session.exec(stmt)).scalar_one()
        await session.commit()
        created = True
        logger.info(f"Anomaly Detection Rule '{rule.name}' Successfully Created")

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


async def db_detect_anomalies_for_pipeline(
    session: Session, pipeline_id: int, pipeline_execution_id: int
):
    logger.info(f"Detecting anomalies for pipeline {pipeline_id}")

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
        AnomalyDetectionRule.name,
        AnomalyDetectionRule.pipeline_id,
        AnomalyDetectionRule.lookback_days,
        AnomalyDetectionRule.minimum_executions,
        AnomalyDetectionRule.metric_field,
        AnomalyDetectionRule.std_deviation_threshold_multiplier,
    ).where(AnomalyDetectionRule.id.in_(rule_ids))

    rules = (await session.exec(rules_query)).all()
    rule_ids.clear()

    for rule in rules:
        try:
            await _detect_anomalies_for_rule(session, rule, pipeline_execution_id)
        except Exception as e:
            logger.error(f"Error detecting anomalies for rule '{rule.name}': {e}")
            continue


async def _detect_anomalies_for_rule(
    session: Session, rule: AnomalyDetectionRule, pipeline_execution_id: int
) -> List[AnomalyDetectionResultOutput]:
    logger.info(
        f"Detecting anomalies for rule '{rule.name}' on pipeline {rule.pipeline_id}"
    )
    lookback_date = pendulum.now("UTC").subtract(days=(rule.lookback_days))

    hour_recorded = (
        await session.exec(
            select(PipelineExecution.hour_recorded).where(
                PipelineExecution.id == pipeline_execution_id
            )
        )
    ).scalar_one()

    ids_query = (
        select(PipelineExecution.id)
        .where(PipelineExecution.pipeline_id == rule.pipeline_id)
        .where(PipelineExecution.hour_recorded == hour_recorded)
        .where(PipelineExecution.end_date >= lookback_date)
        .where(PipelineExecution.end_date.is_not(None))
        .where(PipelineExecution.completed_successfully == True)
    )
    execution_ids = (await session.exec(ids_query)).scalars().all()

    if len(execution_ids) < rule.minimum_executions:
        logger.warning(
            f"Not enough executions for rule '{rule.name}': {len(execution_ids)} < {rule.minimum_executions}"
        )
        return

    # PK seek for execution data
    executions_query = select(
        PipelineExecution.id,
        PipelineExecution.duration_seconds,
        PipelineExecution.total_rows,
        PipelineExecution.inserts,
        PipelineExecution.updates,
        PipelineExecution.soft_deletes,
    ).where(PipelineExecution.id.in_(execution_ids))
    executions = (await session.exec(executions_query)).all()
    execution_ids.clear()

    metric_values = []
    for execution in executions:
        # Access the labeled column directly by name
        metric_value = getattr(execution, rule.metric_field.value)
        if metric_value is not None:
            metric_values.append(metric_value)

    if len(metric_values) < rule.minimum_executions:
        logger.warning(
            f"Not enough metric values for rule '{rule.name}': {len(metric_values)} < {rule.minimum_executions}"
        )
        return

    baseline_mean = statistics.mean(metric_values)
    baseline_std = statistics.stdev(metric_values) if len(metric_values) > 1 else 0
    metric_values.clear()

    # Handle case where std dev is 0 (all values are identical, like 0 rows)
    if baseline_std == 0:
        logger.warning(
            f"No variance in data for rule {rule.name}, skipping anomaly detection"
        )
        return

    # Define anomaly threshold using standard deviations
    threshold = baseline_mean + (rule.std_deviation_threshold_multiplier * baseline_std)

    existing_anomalies_query = select(
        AnomalyDetectionResult.pipeline_execution_id
    ).where(
        AnomalyDetectionResult.rule_id == rule.id,
        AnomalyDetectionResult.pipeline_execution_id.in_(
            [execution.id for execution in executions]
        ),
    )

    existing_anomaly_execution_ids = set(
        (await session.exec(existing_anomalies_query)).scalars().all()
    )

    new_anomaly_results = []
    logger.info(f"Processing {len(executions)} executions for anomaly detection")
    logger.info(
        f"Threshold: {threshold}, Baseline mean: {baseline_mean}, Baseline std: {baseline_std}"
    )

    for execution in executions:
        current_value = getattr(execution, rule.metric_field.value, None)
        if current_value is None:
            continue

        if (
            current_value > threshold
            and execution.id not in existing_anomaly_execution_ids
        ):
            # Calculate z-score (how many standard deviations above mean)
            z_score = (current_value - baseline_mean) / baseline_std
            deviation_percentage = (
                (current_value - baseline_mean) / baseline_mean
            ) * 100

            # Confidence score based on how many std devs beyond the threshold
            confidence_score = min(
                1.0, z_score / rule.std_deviation_threshold_multiplier
            )

            anomaly_result = AnomalyDetectionResult(
                rule_id=rule.id,
                pipeline_execution_id=execution.id,
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

            new_anomaly_results.append(anomaly_result)

    executions.clear()

    if new_anomaly_results:
        session.add_all(new_anomaly_results)
        await session.commit()

        try:
            anomaly_details = []
            for result in new_anomaly_results:
                anomaly_details.append(
                    f"• Execution ID {result.pipeline_execution_id}: "
                    f"{result.violation_value} (baseline: {result.baseline_value:.2f}, "
                    f"deviation: {result.deviation_percentage:.1f}%, "
                    f"confidence: {result.confidence_score:.2f})"
                )

            send_slack_message(
                level=AlertLevel.WARNING,
                message=f"Anomaly detected in pipeline {rule.pipeline_id} - {len(new_anomaly_results)} execution(s) flagged",
                details={
                    "Rule": rule.name,
                    "Metric": rule.metric_field.value,
                    "Threshold Multiplier": rule.std_deviation_threshold_multiplier,
                    "Lookback Days": rule.lookback_days,
                    "Anomalies": "\n".join(anomaly_details),
                },
            )
        except Exception as e:
            logger.error(f"Failed to send Slack notification for anomalies: {e}")

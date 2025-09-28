from fastapi import APIRouter, Response, status
from sqlalchemy import select

from src.database.anomaly_detection_utils import (
    db_get_or_create_anomaly_detection_rule,
    db_update_anomaly_detection_rule,
)
from src.database.models.anomaly_detection import AnomalyDetectionRule
from src.database.session import SessionDep
from src.models.anomaly_detection import (
    AnomalyDetectionRulePatchInput,
    AnomalyDetectionRulePostInput,
    AnomalyDetectionRulePostOutput,
)

router = APIRouter()


@router.post("/anomaly_detection_rule", response_model=AnomalyDetectionRulePostOutput)
async def get_or_create_anomaly_detection_rule(
    rule: AnomalyDetectionRulePostInput, response: Response, session: SessionDep
):
    return await db_get_or_create_anomaly_detection_rule(
        session=session, rule=rule, response=response
    )


@router.get(
    "/anomaly_detection_rule",
    response_model=list[AnomalyDetectionRule],
    status_code=status.HTTP_200_OK,
)
async def get_anomaly_detection_rules(session: SessionDep):
    return (await session.exec(select(AnomalyDetectionRule))).scalars().all()


@router.patch(
    "/anomaly_detection_rule",
    response_model=AnomalyDetectionRule,
    status_code=status.HTTP_200_OK,
)
async def update_anomaly_detection_rule(
    rule: AnomalyDetectionRulePatchInput, session: SessionDep
):
    return await db_update_anomaly_detection_rule(session=session, patch=rule)

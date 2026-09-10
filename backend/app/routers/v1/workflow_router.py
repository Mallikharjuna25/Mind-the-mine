"""
Alerts, Corrective Actions & SLA Escalation Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.workflow_models import Alert, CorrectiveAction, Escalation
from app.schemas.workflow_schemas import (
    AlertResponse, CorrectiveActionCreate, CorrectiveActionVerifyRequest,
    CorrectiveActionResponse, EscalationResponse
)
from app.schemas.common_schemas import ApiResponse
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/mine", tags=["Alerts & Remediation Workflows"])


@router.get("/alerts", response_model=ApiResponse[List[AlertResponse]])
async def list_alerts(
    mine_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if mine_id:
        stmt = stmt.where(Alert.mine_id == mine_id)
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter)
    if severity:
        stmt = stmt.where(Alert.severity == severity)

    res = await db.execute(stmt)
    alerts = list(res.scalars().all())
    return ApiResponse(data=[AlertResponse.model_validate(a) for a in alerts])


@router.post("/alerts/{alert_id}/acknowledge", response_model=ApiResponse[AlertResponse])
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("alert.acknowledge"))
):
    alert = await workflow_service.acknowledge_alert(db=db, alert_id=alert_id, user_id=current_user.sub)
    return ApiResponse(message="Alert acknowledged. SLA timer stopped.", data=AlertResponse.model_validate(alert))


@router.post("/corrective-actions", response_model=ApiResponse[CorrectiveActionResponse])
async def create_corrective_action(
    payload: CorrectiveActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("action.create"))
):
    action = await workflow_service.create_corrective_action(db=db, payload=payload, user_id=current_user.sub)
    return ApiResponse(message="Corrective action created and assigned", data=CorrectiveActionResponse.model_validate(action))


@router.post("/corrective-actions/{action_id}/verify", response_model=ApiResponse[CorrectiveActionResponse])
async def verify_corrective_action(
    action_id: str,
    payload: CorrectiveActionVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("action.verify"))
):
    action = await workflow_service.verify_and_close_action(
        db=db,
        action_id=action_id,
        payload=payload,
        user_id=current_user.sub
    )
    return ApiResponse(message=f"Action marked as {action.status}", data=CorrectiveActionResponse.model_validate(action))


@router.get("/escalations", response_model=ApiResponse[List[EscalationResponse]])
async def list_escalations(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("escalation.read"))
):
    stmt = select(Escalation).order_by(Escalation.triggered_at.desc())
    res = await db.execute(stmt)
    escalations = list(res.scalars().all())
    return ApiResponse(data=[EscalationResponse.model_validate(e) for e in escalations])


@router.post("/escalations/evaluate-sla", response_model=ApiResponse[List[EscalationResponse]])
async def evaluate_sla_timers(db: AsyncSession = Depends(get_db)):
    """
    Evaluates 5-minute SLA timer check and escalates unacknowledged high/critical alerts.
    """
    escalations = await workflow_service.evaluate_sla_escalations(db=db)
    return ApiResponse(message=f"Triggered {len(escalations)} SLA escalations", data=[EscalationResponse.model_validate(e) for e in escalations])

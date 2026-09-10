"""
Compliance & Violation Verification Router
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.compliance_models import Violation
from app.schemas.compliance_schemas import ViolationResponse, ViolationVerifyRequest
from app.schemas.common_schemas import ApiResponse
from app.services.audit_service import audit_service
from app.services.risk_engine_service import risk_engine_service

router = APIRouter(prefix="/mine", tags=["Compliance & Violations"])


@router.get("/violations", response_model=ApiResponse[List[ViolationResponse]])
async def list_violations(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Violation).order_by(Violation.created_at.desc())
    if mine_id:
        stmt = stmt.where(Violation.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(Violation.zone_id == zone_id)
    if category:
        stmt = stmt.where(Violation.category == category)
    if severity:
        stmt = stmt.where(Violation.severity == severity)
    if status_filter:
        stmt = stmt.where(Violation.status == status_filter)

    res = await db.execute(stmt)
    violations = list(res.scalars().all())
    return ApiResponse(data=[ViolationResponse.model_validate(v) for v in violations])


@router.get("/violations/{violation_id}", response_model=ApiResponse[ViolationResponse])
async def get_violation_details(violation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Violation).where(Violation.id == violation_id)
    res = await db.execute(stmt)
    v = res.scalars().first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")
    return ApiResponse(data=ViolationResponse.model_validate(v))


@router.post("/violations/{violation_id}/verify", response_model=ApiResponse[ViolationResponse])
async def verify_violation(
    violation_id: str,
    payload: ViolationVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("compliance.violation.verify"))
):
    """
    Officer human-in-the-loop decision: CONFIRMED or REJECTED
    """
    stmt = select(Violation).where(Violation.id == violation_id)
    res = await db.execute(stmt)
    violation = res.scalars().first()
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")

    decision = payload.decision.upper()
    if decision not in ("CONFIRMED", "REJECTED"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Decision must be CONFIRMED or REJECTED")

    violation.status = decision
    violation.verified_by_user_id = current_user.sub
    violation.verified_at = datetime.now(timezone.utc)
    if payload.rejection_reason:
        violation.rejection_reason = payload.rejection_reason
    if payload.adjusted_severity:
        violation.severity = payload.adjusted_severity
    if payload.rule_reference:
        violation.rule_reference = payload.rule_reference

    await audit_service.log_action(
        db=db,
        action=f"VIOLATION_{decision}",
        entity_type="Violation",
        entity_id=violation.id,
        changes={"decision": decision, "reason": payload.rejection_reason},
        user_id=current_user.sub,
        user_email=current_user.email,
        mine_id=violation.mine_id
    )

    await db.commit()
    await db.refresh(violation)

    # Recompute risk for zone asynchronously
    await risk_engine_service.compute_zone_risk(db, violation.mine_id, violation.zone_id)

    return ApiResponse(message=f"Violation {violation.violation_code} marked as {decision}", data=ViolationResponse.model_validate(violation))

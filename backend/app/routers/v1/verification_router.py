from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.module2_models import FieldVerification
from backend.app.schemas.module2_schemas import (
    FieldVerificationResponse, FieldVerificationUpdate
)
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/field-verifications", tags=["Field Verification & Remediation"])

VALID_TRANSITIONS = {
    "REPORTED": ["VERIFIED"],
    "VERIFIED": ["CORRECTIVE_ACTION"],
    "CORRECTIVE_ACTION": ["EVIDENCE_SUBMITTED"],
    "EVIDENCE_SUBMITTED": ["SUPERVISOR_REVIEW"],
    "SUPERVISOR_REVIEW": ["APPROVED", "CORRECTIVE_ACTION"],
    "APPROVED": ["CLOSED"],
    "CLOSED": []
}

@router.get("", response_model=List[FieldVerificationResponse])
def get_verifications(
    mine_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(FieldVerification)
    if mine_id:
        query = query.filter(FieldVerification.mine_id == mine_id)
    if status:
        query = query.filter(FieldVerification.status == status)
    return query.order_by(FieldVerification.created_at.desc()).all()

@router.get("/{verification_id}", response_model=FieldVerificationResponse)
def get_verification_by_id(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    ver = db.query(FieldVerification).filter(FieldVerification.id == verification_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="Verification task not found")
    return ver

@router.patch("/{verification_id}/transition", response_model=FieldVerificationResponse)
def transition_verification_state(
    verification_id: str,
    update_in: FieldVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    ver = db.query(FieldVerification).filter(FieldVerification.id == verification_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="Verification record not found")

    target_status = update_in.status
    allowed = VALID_TRANSITIONS.get(ver.status, [])
    if target_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {ver.status} to {target_status}. Allowed: {allowed}"
        )

    ver.status = target_status
    if update_in.remediation_notes:
        ver.remediation_notes = update_in.remediation_notes
    if update_in.after_evidence_urls:
        ver.after_evidence_urls = update_in.after_evidence_urls
    if update_in.supervisor_notes:
        ver.supervisor_notes = update_in.supervisor_notes

    if target_status == "VERIFIED":
        ver.verified_by = current_user["user_id"]
        ver.verified_at = datetime.now(timezone.utc)
    elif target_status == "CLOSED":
        ver.closed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ver)

    AuditService.log_event(db, "VERIFICATION", ver.id, f"TRANSITION_{target_status}", current_user["user_id"], {
        "previous_status": ver.status, "new_status": target_status
    })

    return ver

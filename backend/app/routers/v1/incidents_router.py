from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_sync_db
from app.core.security import get_current_user
from app.models.module2_models import IncidentRecord, FieldVerification
from app.schemas.module2_schemas import IncidentRecordCreate, IncidentRecordResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentRecordResponse])
def get_incidents(
    mine_id: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_sync_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(IncidentRecord)
    if mine_id:
        query = query.filter(IncidentRecord.mine_id == mine_id)
    if severity:
        query = query.filter(IncidentRecord.severity == severity)
    return query.order_by(IncidentRecord.created_at.desc()).all()

@router.post("", response_model=IncidentRecordResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    inc_in: IncidentRecordCreate,
    db: Session = Depends(get_sync_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.query(IncidentRecord).filter(IncidentRecord.client_id == inc_in.client_id).first()
    if existing:
        return existing

    incident = IncidentRecord(
        client_id=inc_in.client_id,
        mine_id=inc_in.mine_id,
        zone_id=inc_in.zone_id,
        reporter_id=current_user["user_id"],
        incident_type=inc_in.incident_type,
        severity=inc_in.severity,
        occurrence_time=inc_in.occurrence_time,
        location_name=inc_in.location_name,
        latitude=inc_in.latitude,
        longitude=inc_in.longitude,
        accuracy=inc_in.accuracy,
        description=inc_in.description,
        people_involved=inc_in.people_involved,
        witnesses=inc_in.witnesses,
        immediate_action=inc_in.immediate_action,
        evidence_urls=inc_in.evidence_urls,
        status="REPORTED"
    )
    db.add(incident)
    db.flush()

    # Automatically create field verification workflow task
    verification = FieldVerification(
        issue_type="INCIDENT",
        source_id=incident.id,
        mine_id=inc_in.mine_id,
        status="REPORTED",
        remediation_notes=f"Incident: {inc_in.incident_type} (Severity: {inc_in.severity}). Action taken: {inc_in.immediate_action}",
        before_evidence_urls=inc_in.evidence_urls
    )
    db.add(verification)

    db.commit()
    db.refresh(incident)

    AuditService.log_event(db, "INCIDENT", incident.id, "CREATED", current_user["user_id"], {
        "type": incident.incident_type, "severity": incident.severity
    })

    return incident

@router.get("/{incident_id}", response_model=IncidentRecordResponse)
def get_incident_by_id(incident_id: str, db: Session = Depends(get_sync_db), current_user: dict = Depends(get_current_user)):
    incident = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

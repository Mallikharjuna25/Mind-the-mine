from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.module2_models import FieldReport
from backend.app.schemas.module2_schemas import FieldReportCreate, FieldReportResponse
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/field-reports", tags=["Field Reports"])

@router.get("", response_model=List[FieldReportResponse])
def get_field_reports(
    mine_id: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(FieldReport)
    if mine_id:
        query = query.filter(FieldReport.mine_id == mine_id)
    if category:
        query = query.filter(FieldReport.category == category)
    if severity:
        query = query.filter(FieldReport.severity == severity)
    return query.order_by(FieldReport.created_at.desc()).all()

@router.post("", response_model=FieldReportResponse, status_code=status.HTTP_201_CREATED)
def create_field_report(
    report_in: FieldReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check idempotency
    existing = db.query(FieldReport).filter(FieldReport.client_id == report_in.client_id).first()
    if existing:
        return existing

    report = FieldReport(
        client_id=report_in.client_id,
        mine_id=report_in.mine_id,
        zone_id=report_in.zone_id,
        officer_id=current_user["user_id"],
        category=report_in.category,
        severity=report_in.severity,
        description=report_in.description,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        accuracy=report_in.accuracy,
        capture_timestamp=report_in.capture_timestamp,
        evidence_urls=report_in.evidence_urls,
        status="REPORTED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    AuditService.log_event(db, "FIELD_REPORT", report.id, "CREATED", current_user["user_id"], {
        "category": report.category, "severity": report.severity
    })

    return report

@router.get("/{report_id}", response_model=FieldReportResponse)
def get_field_report_by_id(report_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Field report not found")
    return report

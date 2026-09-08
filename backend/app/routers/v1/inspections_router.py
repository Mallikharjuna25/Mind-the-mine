from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.module2_models import InspectionTemplate, InspectionAudit, FieldVerification
from backend.app.schemas.module2_schemas import (
    InspectionTemplateResponse, InspectionAuditCreate, InspectionAuditResponse
)
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/inspections", tags=["Inspections"])

# Seed templates if not exist
DEFAULT_TEMPLATES = [
    {
        "id": "TMPL-DGMS-FIRE-01",
        "title": "DGMS Fire Safety & Gas Inundation Inspection",
        "category": "FIRE_SAFETY",
        "description": "Standard Coal Mines Regulations statutory fire prevention and ventilation audit.",
        "items": [
            {"item_code": "FIRE-01", "question": "Are portable fire extinguishers charged and within annual inspection date?", "category": "FIRE", "mandatory": True, "requires_photo": True},
            {"item_code": "FIRE-02", "question": "Is stone dust barrier properly maintained in accordance with DGMS norms?", "category": "EXPLOSION", "mandatory": True, "requires_photo": False},
            {"item_code": "FIRE-03", "question": "Are emergency water spray hydrants operational along conveyor transfer points?", "category": "SUPPRESSION", "mandatory": True, "requires_photo": True},
            {"item_code": "FIRE-04", "question": "Are flameproof electrical enclosures properly bolted and sealed?", "category": "ELECTRICAL", "mandatory": True, "requires_photo": True},
            {"item_code": "FIRE-05", "question": "Are emergency escape routes clearly illuminated and free from obstructions?", "category": "EVACUATION", "mandatory": True, "requires_photo": False}
        ],
        "version": "1.0"
    },
    {
        "id": "TMPL-ENV-MON-02",
        "title": "MoEFCC Environmental & Dust Compliance Audit",
        "category": "ENVIRONMENTAL",
        "description": "Environmental monitoring covering water sprinkling, dust suppression, and drainage.",
        "items": [
            {"item_code": "ENV-01", "question": "Are haul road water tankers actively running to suppress coal dust?", "category": "AIR_QUALITY", "mandatory": True, "requires_photo": True},
            {"item_code": "ENV-02", "question": "Are settling pond silt traps functioning and preventing acidic runoff?", "category": "WATER", "mandatory": True, "requires_photo": False},
            {"item_code": "ENV-03", "question": "Is ambient noise barrier in place near active blasting and residential zones?", "category": "NOISE", "mandatory": False, "requires_photo": False}
        ],
        "version": "1.0"
    },
    {
        "id": "TMPL-HEMM-STAT-03",
        "title": "HEMM Heavy Earthmoving Machinery Pre-Shift Audit",
        "category": "MACHINERY",
        "description": "Mechanical integrity, brake tests, audio-visual reverse alarms, and seatbelt checks.",
        "items": [
            {"item_code": "HEMM-01", "question": "Is the Audio-Visual Alarm (AWA) functioning when reverse gear is engaged?", "category": "SAFETY_DEVICE", "mandatory": True, "requires_photo": False},
            {"item_code": "HEMM-02", "question": "Are service and emergency brakes tested and meeting stopping distance specifications?", "category": "BRAKES", "mandatory": True, "requires_photo": True},
            {"item_code": "HEMM-03", "question": "Are hydraulic lines free from leaks, chafing, or high pressure bulging?", "category": "HYDRAULICS", "mandatory": True, "requires_photo": True}
        ],
        "version": "1.0"
    }
]

@router.get("/templates", response_model=List[InspectionTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(InspectionTemplate).all()
    if not templates:
        for t in DEFAULT_TEMPLATES:
            tmpl = InspectionTemplate(
                id=t["id"],
                title=t["title"],
                category=t["category"],
                description=t["description"],
                items=t["items"],
                version=t["version"]
            )
            db.add(tmpl)
        db.commit()
        templates = db.query(InspectionTemplate).all()
    return templates

@router.get("", response_model=List[InspectionAuditResponse])
def get_inspections(
    mine_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(InspectionAudit)
    if mine_id:
        query = query.filter(InspectionAudit.mine_id == mine_id)
    if status:
        query = query.filter(InspectionAudit.status == status)
    return query.order_by(InspectionAudit.created_at.desc()).all()

@router.post("", response_model=InspectionAuditResponse, status_code=status.HTTP_201_CREATED)
def submit_inspection(
    audit_in: InspectionAuditCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.query(InspectionAudit).filter(InspectionAudit.client_id == audit_in.client_id).first()
    if existing:
        return existing

    failed_items = [it for it in audit_in.items_results if it.result_status == "FAIL"]
    passed_items = [it for it in audit_in.items_results if it.result_status == "PASS"]
    score = 100.0
    if len(audit_in.items_results) > 0:
        score = round((len(passed_items) / max(1, len(passed_items) + len(failed_items))) * 100.0, 1)

    audit = InspectionAudit(
        client_id=audit_in.client_id,
        template_id=audit_in.template_id,
        mine_id=audit_in.mine_id,
        zone_id=audit_in.zone_id,
        inspector_id=current_user["user_id"],
        scheduled_date=audit_in.scheduled_date,
        shift=audit_in.shift,
        status="SUBMITTED",
        overall_score=score,
        summary_findings=audit_in.summary_findings,
        items_results=[it.model_dump() for it in audit_in.items_results]
    )
    db.add(audit)
    db.flush()

    for failed in failed_items:
        verification = FieldVerification(
            issue_type="INSPECTION_FAIL",
            source_id=audit.id,
            mine_id=audit_in.mine_id,
            status="REPORTED",
            remediation_notes=f"Failed [{failed.item_code}]: {failed.question}. Observation: {failed.observation}",
            before_evidence_urls=failed.evidence_urls
        )
        db.add(verification)

    db.commit()
    db.refresh(audit)

    AuditService.log_event(db, "INSPECTION", audit.id, "SUBMITTED", current_user["user_id"], {
        "score": score, "failed_count": len(failed_items)
    })

    return audit

@router.get("/{audit_id}", response_model=InspectionAuditResponse)
def get_inspection_by_id(audit_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    audit = db.query(InspectionAudit).filter(InspectionAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return audit

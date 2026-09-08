from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.module2_models import AIIncidentStructuringLog
from backend.app.schemas.module2_schemas import AIStructureRequest, AIStructureResponse
from backend.app.services.ai_structuring_service import AIIncidentStructuringService

router = APIRouter(prefix="/ai", tags=["AI Assistive Structuring"])

@router.post("/structure-incident", response_model=AIStructureResponse)
def structure_incident_notes(
    req: AIStructureRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    analysis = AIIncidentStructuringService.structure_unstructured_input(req.raw_text)

    # Persist log for AI governance audit trail
    log = AIIncidentStructuringLog(
        raw_input=req.raw_text,
        suggested_incident_type=analysis["suggested_incident_type"],
        suggested_severity=analysis["suggested_severity"],
        suggested_hazard=analysis["suggested_hazard"],
        suggested_location=analysis["suggested_location"],
        suggested_injury=analysis["suggested_injury"],
        confidence_score=analysis["confidence_score"],
        confirmed_by=current_user["user_id"]
    )
    db.add(log)
    db.commit()

    return AIStructureResponse(
        raw_text=req.raw_text,
        suggested_incident_type=analysis["suggested_incident_type"],
        suggested_severity=analysis["suggested_severity"],
        suggested_hazard=analysis["suggested_hazard"],
        suggested_location=analysis["suggested_location"],
        suggested_injury=analysis["suggested_injury"],
        confidence_score=analysis["confidence_score"],
        reasoning=analysis["reasoning"]
    )

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_sync_db
from app.core.security import get_current_user
from app.models.module2_models import FieldReport, IncidentRecord, InspectionAudit
from app.schemas.module2_schemas import GISFeatureCollection, GISFeature

router = APIRouter(prefix="/gis", tags=["GIS Handoff"])

@router.get("/features", response_model=GISFeatureCollection)
def get_gis_features(
    mine_id: Optional[str] = "MINE-DHANBAD-01",
    db: Session = Depends(get_sync_db),
    current_user: dict = Depends(get_current_user)
):
    features: List[GISFeature] = []

    # 1. Field Reports
    reports = db.query(FieldReport).filter(FieldReport.latitude != None, FieldReport.longitude != None).all()
    for r in reports:
        features.append(GISFeature(
            type="Feature",
            geometry={
                "type": "Point",
                "coordinates": [r.longitude, r.latitude]
            },
            properties={
                "id": r.id,
                "layer": "FIELD_REPORTS",
                "category": r.category,
                "severity": r.severity,
                "description": r.description,
                "accuracy": r.accuracy,
                "officer_id": r.officer_id,
                "status": r.status
            }
        ))

    # 2. Incidents
    incidents = db.query(IncidentRecord).filter(IncidentRecord.latitude != None, IncidentRecord.longitude != None).all()
    for inc in incidents:
        features.append(GISFeature(
            type="Feature",
            geometry={
                "type": "Point",
                "coordinates": [inc.longitude, inc.latitude]
            },
            properties={
                "id": inc.id,
                "layer": "INCIDENTS",
                "type": inc.incident_type,
                "severity": inc.severity,
                "location_name": inc.location_name,
                "reporter_id": inc.reporter_id,
                "status": inc.status
            }
        ))

    return GISFeatureCollection(features=features)

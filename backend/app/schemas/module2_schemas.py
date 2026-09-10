from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Field Report Schemas ---
class FieldReportCreate(BaseModel):
    client_id: str
    mine_id: str
    zone_id: Optional[str] = None
    category: str
    severity: str = "MEDIUM"
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    capture_timestamp: Optional[datetime] = None
    evidence_urls: List[str] = []

class FieldReportResponse(BaseModel):
    id: str
    client_id: str
    mine_id: str
    zone_id: Optional[str] = None
    officer_id: str
    category: str
    severity: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    capture_timestamp: Optional[datetime] = None
    evidence_urls: List[str] = []
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Inspection Checklist Schemas ---
class ChecklistItemResultSchema(BaseModel):
    item_code: str
    question: str
    result_status: str # PASS, FAIL, NA
    observation: Optional[str] = ""
    severity: Optional[str] = "LOW"
    evidence_urls: List[str] = []
    incident_generated: bool = False

class InspectionAuditCreate(BaseModel):
    client_id: str
    template_id: str
    mine_id: str
    zone_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    shift: str = "SHIFT_A"
    summary_findings: Optional[str] = ""
    items_results: List[ChecklistItemResultSchema] = []

class InspectionAuditResponse(BaseModel):
    id: str
    client_id: str
    template_id: str
    mine_id: str
    zone_id: Optional[str] = None
    inspector_id: str
    scheduled_date: datetime
    shift: str
    status: str
    overall_score: float
    summary_findings: Optional[str] = None
    items_results: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class InspectionTemplateResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str]
    items: List[Dict[str, Any]]
    version: str

    class Config:
        from_attributes = True

# --- Incident Schemas ---
class IncidentRecordCreate(BaseModel):
    client_id: str
    mine_id: str
    zone_id: Optional[str] = None
    incident_type: str
    severity: str = "MODERATE"
    occurrence_time: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    description: str
    people_involved: List[str] = []
    witnesses: List[str] = []
    immediate_action: Optional[str] = None
    evidence_urls: List[str] = []

class IncidentRecordResponse(BaseModel):
    id: str
    client_id: str
    mine_id: str
    zone_id: Optional[str] = None
    reporter_id: str
    incident_type: str
    severity: str
    occurrence_time: datetime
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    description: str
    people_involved: List[str] = []
    witnesses: List[str] = []
    immediate_action: Optional[str] = None
    evidence_urls: List[str] = []
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- AI Structuring Schemas ---
class AIStructureRequest(BaseModel):
    raw_text: str
    mine_id: Optional[str] = "MINE-DHANBAD-01"
    zone_id: Optional[str] = None

class AIStructureResponse(BaseModel):
    raw_text: str
    suggested_incident_type: str
    suggested_severity: str
    suggested_hazard: str
    suggested_location: str
    suggested_injury: str
    confidence_score: float
    reasoning: str

# --- Verification & Corrective Actions ---
class FieldVerificationCreate(BaseModel):
    issue_type: str # FIELD_REPORT, INSPECTION_FAIL, INCIDENT
    source_id: str
    mine_id: str
    assigned_to: Optional[str] = None
    remediation_notes: Optional[str] = None
    before_evidence_urls: List[str] = []

class FieldVerificationUpdate(BaseModel):
    status: str # CORRECTIVE_ACTION, EVIDENCE_SUBMITTED, SUPERVISOR_REVIEW, APPROVED, CLOSED
    remediation_notes: Optional[str] = None
    after_evidence_urls: Optional[List[str]] = None
    supervisor_notes: Optional[str] = None

class FieldVerificationResponse(BaseModel):
    id: str
    issue_type: str
    source_id: str
    mine_id: str
    status: str
    assigned_to: Optional[str] = None
    remediation_notes: Optional[str] = None
    before_evidence_urls: List[str] = []
    after_evidence_urls: List[str] = []
    supervisor_notes: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Batch Sync Engine Schemas ---
class BatchSyncRequest(BaseModel):
    officer_id: str
    sync_timestamp: datetime
    field_reports: List[FieldReportCreate] = []
    inspections: List[InspectionAuditCreate] = []
    incidents: List[IncidentRecordCreate] = []

class BatchSyncResultItem(BaseModel):
    client_id: str
    server_id: str
    entity_type: str
    status: str # SYNCED, CONFLICT, REJECTED
    message: str

class BatchSyncResponse(BaseModel):
    success: bool
    synced_at: datetime
    processed_count: int
    results: List[BatchSyncResultItem]

# --- GIS Features ---
class GISFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]

class GISFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GISFeature]

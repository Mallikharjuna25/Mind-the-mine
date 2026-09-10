import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class FieldReport(Base):
    __tablename__ = "module2_field_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    client_id = Column(String(64), unique=True, index=True, nullable=False)
    mine_id = Column(String(64), index=True, nullable=False)
    zone_id = Column(String(64), nullable=True)
    officer_id = Column(String(64), index=True, nullable=False)
    category = Column(String(64), nullable=False)  # HAZARD, SAFETY_OBSERVATION, VIOLATION, etc.
    severity = Column(String(32), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    capture_timestamp = Column(DateTime, default=utc_now)
    evidence_urls = Column(JSON, default=list) # List of image/audio/video URLs
    status = Column(String(32), default="REPORTED") # REPORTED, VERIFIED, ACTION_REQUIRED, CLOSED
    sync_state = Column(String(32), default="SYNCED")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class InspectionTemplate(Base):
    __tablename__ = "module2_inspection_templates"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False) # STATUTORY, FIRE_SAFETY, ENVIRONMENTAL, MACHINERY
    description = Column(Text, nullable=True)
    items = Column(JSON, default=list) # [{item_code, question, category, mandatory, requires_photo}]
    version = Column(String(16), default="1.0")
    created_at = Column(DateTime, default=utc_now)

class InspectionAudit(Base):
    __tablename__ = "module2_inspection_audits"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    client_id = Column(String(64), unique=True, index=True, nullable=False)
    template_id = Column(String(64), nullable=False)
    mine_id = Column(String(64), index=True, nullable=False)
    zone_id = Column(String(64), nullable=True)
    inspector_id = Column(String(64), index=True, nullable=False)
    scheduled_date = Column(DateTime, default=utc_now)
    shift = Column(String(32), default="SHIFT_A")
    status = Column(String(32), default="SUBMITTED") # PLANNED, ASSIGNED, IN_PROGRESS, SUBMITTED, VERIFIED, CLOSED
    overall_score = Column(Float, default=100.0)
    summary_findings = Column(Text, nullable=True)
    items_results = Column(JSON, default=list) # [{item_code, question, result_status: PASS/FAIL/NA, observation, evidence_urls}]
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class IncidentRecord(Base):
    __tablename__ = "module2_incident_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    client_id = Column(String(64), unique=True, index=True, nullable=False)
    mine_id = Column(String(64), index=True, nullable=False)
    zone_id = Column(String(64), nullable=True)
    reporter_id = Column(String(64), index=True, nullable=False)
    incident_type = Column(String(64), nullable=False) # ACCIDENT, INJURY, FIRE, EQUIPMENT_FAILURE, etc.
    severity = Column(String(32), default="MODERATE") # MINOR, MODERATE, MAJOR, FATAL, CRITICAL
    occurrence_time = Column(DateTime, default=utc_now)
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    description = Column(Text, nullable=False)
    people_involved = Column(JSON, default=list)
    witnesses = Column(JSON, default=list)
    immediate_action = Column(Text, nullable=True)
    evidence_urls = Column(JSON, default=list)
    status = Column(String(32), default="REPORTED") # REPORTED, VERIFIED, ACTION_REQUIRED, CLOSED
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class AIIncidentStructuringLog(Base):
    __tablename__ = "module2_ai_structuring_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    incident_id = Column(String(36), nullable=True)
    raw_input = Column(Text, nullable=False)
    suggested_incident_type = Column(String(64), nullable=True)
    suggested_severity = Column(String(32), nullable=True)
    suggested_hazard = Column(String(128), nullable=True)
    suggested_location = Column(String(128), nullable=True)
    suggested_injury = Column(String(64), nullable=True)
    confidence_score = Column(Float, default=0.90)
    confirmed_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utc_now)

class FieldVerification(Base):
    __tablename__ = "module2_field_verifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    issue_type = Column(String(64), nullable=False) # FIELD_REPORT, INSPECTION_FAIL, INCIDENT
    source_id = Column(String(64), nullable=False, index=True)
    mine_id = Column(String(64), index=True, nullable=False)
    status = Column(String(32), default="REPORTED") # REPORTED, VERIFIED, CORRECTIVE_ACTION, EVIDENCE_SUBMITTED, SUPERVISOR_REVIEW, APPROVED, CLOSED
    assigned_to = Column(String(64), nullable=True)
    remediation_notes = Column(Text, nullable=True)
    before_evidence_urls = Column(JSON, default=list)
    after_evidence_urls = Column(JSON, default=list)
    supervisor_notes = Column(Text, nullable=True)
    verified_by = Column(String(64), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class AuditTrailEntry(Base):
    __tablename__ = "module2_audit_trail"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    performed_by = Column(String(64), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=utc_now)
    sha256_hash = Column(String(64), nullable=True)

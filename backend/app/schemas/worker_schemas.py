"""
Worker & Compliance Management Pydantic Schemas (Module 3 -> Task 2)
Defines validation schemas for Worker Registry, Attendance, Training, Certifications, PPE, Authorization & Reports.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class WorkerCreate(BaseModel):
    mine_id: str
    contractor_id: Optional[str] = None
    employee_id: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    department: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = None
    phone: str = Field(..., min_length=5, max_length=50)
    emergency_contact_name: str = Field(..., min_length=2, max_length=100)
    emergency_contact_phone: str = Field(..., min_length=5, max_length=50)
    joining_date: date
    status: str = Field(default="ACTIVE")


class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    contractor_id: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    status: Optional[str] = None


class WorkerAttendanceCreate(BaseModel):
    shift: str = Field(..., description="MORNING, AFTERNOON, NIGHT")
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str = Field(default="PRESENT", description="PRESENT, ABSENT, LATE, LEAVE, OVERTIME")


class WorkerAttendanceResponse(BaseModel):
    id: str
    worker_id: str
    mine_id: str
    shift: str
    check_in: datetime
    check_out: Optional[datetime] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerTrainingCreate(BaseModel):
    program_name: str = Field(..., min_length=2, max_length=255)
    trainer_name: str = Field(..., min_length=2, max_length=100)
    completed_date: date
    expiry_date: date
    status: str = Field(default="COMPLETED")


class WorkerTrainingResponse(BaseModel):
    id: str
    worker_id: str
    program_name: str
    trainer_name: str
    completed_date: date
    expiry_date: date
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerCertificationCreate(BaseModel):
    certificate_name: str = Field(..., min_length=2, max_length=255)
    certificate_number: str = Field(..., min_length=2, max_length=100)
    issuing_authority: str = Field(..., min_length=2, max_length=100)
    valid_from: date
    expiry_date: date
    file_path: Optional[str] = None
    verification_status: str = Field(default="VERIFIED")


class WorkerCertificationResponse(BaseModel):
    id: str
    worker_id: str
    certificate_name: str
    certificate_number: str
    issuing_authority: str
    file_path: Optional[str] = None
    valid_from: date
    expiry_date: date
    verification_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerPPECreate(BaseModel):
    item_type: str = Field(..., description="HELMET, HIGH_VIS_VEST, SAFETY_BOOTS, RESPIRATOR, HARNESS, GOGGLES")
    issuance_date: date
    expiry_date: date
    compliance_status: str = Field(default="COMPLIANT", description="COMPLIANT, EXPIRED, PENDING_ISSUANCE, REPLACEMENT_REQUIRED")
    remarks: Optional[str] = None


class WorkerPPEResponse(BaseModel):
    id: str
    worker_id: str
    item_type: str
    issuance_date: date
    expiry_date: date
    compliance_status: str
    remarks: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerAuthorizationCreate(BaseModel):
    zone_id: str = Field(..., min_length=2, max_length=100)
    permit_type: str = Field(..., description="HOT_WORK, UNDERGROUND_ENTRY, CONFINED_SPACE, HIGH_VOLTAGE")
    grant_date: date
    expiry_date: date
    granted_by: str = Field(..., min_length=2, max_length=100)
    status: str = Field(default="GRANTED")


class WorkerAuthorizationResponse(BaseModel):
    id: str
    worker_id: str
    zone_id: str
    permit_type: str
    grant_date: date
    expiry_date: date
    status: str
    granted_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerInsuranceCreate(BaseModel):
    policy_provider: str = Field(..., min_length=2, max_length=255)
    policy_number: str = Field(..., min_length=2, max_length=100)
    policy_type: str = Field(default="ACCIDENTAL_DEATH_DISABILITY")
    coverage_amount: float = Field(..., ge=0)
    start_date: date
    expiry_date: date
    nominee_name: str = Field(..., min_length=2, max_length=100)
    nominee_relation: str = Field(..., min_length=2, max_length=50)
    premium_status: str = Field(default="ACTIVE")
    tpa_contact_number: Optional[str] = None


class WorkerInsuranceResponse(BaseModel):
    id: str
    worker_id: str
    policy_provider: str
    policy_number: str
    policy_type: str
    coverage_amount: float
    start_date: date
    expiry_date: date
    nominee_name: str
    nominee_relation: str
    premium_status: str
    tpa_contact_number: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerLeaveCreate(BaseModel):
    leave_type: str = Field(..., description="CASUAL, SICK_MEDICAL, PRIVILEGE_EARNED, GATE_PASS_SHIFT_EXIT")
    start_date: date
    end_date: date
    days_count: float = Field(default=1.0, ge=0.5)
    reason: str = Field(..., min_length=3)


class WorkerLeaveAction(BaseModel):
    status: str = Field(..., description="APPROVED, REJECTED")
    supervisor_remarks: Optional[str] = None


class WorkerLeaveResponse(BaseModel):
    id: str
    worker_id: str
    mine_id: str
    leave_type: str
    start_date: date
    end_date: date
    days_count: float
    reason: str
    status: str
    approved_by: Optional[str] = None
    supervisor_remarks: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerPassCreate(BaseModel):
    rfid_uid: str = Field(..., min_length=4, max_length=100)
    pass_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    access_level: str = Field(default="GENERAL_SURFACE")  # GENERAL_SURFACE, HAUL_ROAD, DEEP_PIT, UNDERGROUND, BLASTING_ZONE
    permitted_zones: List[str] = Field(default_factory=list)


class WorkerPassAction(BaseModel):
    action: str = Field(..., description="RENEW, SUSPEND, BLOCK, REVOKE, REPLACE")
    revocation_reason: Optional[str] = None
    new_expiry_date: Optional[date] = None
    new_rfid_uid: Optional[str] = None


class WorkerPassResponse(BaseModel):
    id: str
    worker_id: str
    mine_id: str
    rfid_uid: str
    pass_number: str
    issue_date: date
    expiry_date: date
    status: str
    access_level: str
    permitted_zones: List[str]
    last_seen: Optional[datetime] = None
    issued_by: str
    revoked_by: Optional[str] = None
    revocation_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerDocumentResponse(BaseModel):
    id: str
    worker_id: Optional[str] = None
    contractor_id: Optional[str] = None
    document_type: str
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    file_path: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    ocr_status: str
    ocr_confidence: float
    raw_ocr_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[str]] = None
    verification_status: str
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerDocumentReviewAction(BaseModel):
    decision: str = Field(..., description="APPROVE, EDIT_AND_APPROVE, REJECT, REQUEST_REUPLOAD")
    rejection_reason: Optional[str] = None
    corrected_data: Optional[Dict[str, Any]] = None


class WorkerInductionCreate(BaseModel):
    induction_type: str = Field(default="INITIAL_STATUTORY")
    training_title: str = Field(..., min_length=3, max_length=255)
    trainer_name: str = Field(..., min_length=2, max_length=100)
    training_date: date
    validity_months: int = Field(default=12, ge=1, le=60)
    score_percent: Optional[float] = Field(default=90.0, ge=0, le=100)
    remarks: Optional[str] = None


class WorkerInductionResponse(BaseModel):
    id: str
    worker_id: str
    mine_id: str
    induction_type: str
    training_title: str
    trainer_name: str
    training_date: date
    validity_months: int
    expiry_date: date
    score_percent: Optional[float] = None
    certificate_document_id: Optional[str] = None
    verification_status: str
    status: str
    remarks: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerInductionStats(BaseModel):
    total_workers: int
    inducted_count: int
    pending_induction_count: int
    expiring_soon_count: int
    expired_count: int
    safety_cleared_count: int


class WorkerZoneClearanceResponse(BaseModel):
    worker_id: str
    worker_name: str
    zone_id: str
    zone_name: str
    is_access_eligible: bool
    clearance_status: str  # "CLEARED", "RESTRICTED", "BLOCKED"
    checks: Dict[str, Any]  # Details of worker_active, pass_active, induction_valid, ppe_compliant, zone_authorized
    blocking_reasons: List[str]


class WorkerResponse(BaseModel):
    id: str
    mine_id: str
    contractor_id: Optional[str] = None
    employee_id: str
    full_name: str
    department: str
    role: str
    email: Optional[str] = None
    phone: str
    emergency_contact_name: str
    emergency_contact_phone: str
    joining_date: date
    status: str
    blood_group: Optional[str] = "O+"
    rfid_tag: Optional[str] = None
    medical_fitness_status: Optional[str] = "FIT"
    medical_exam_date: Optional[date] = None
    medical_expiry_date: Optional[date] = None
    attendances: List[WorkerAttendanceResponse] = []
    trainings: List[WorkerTrainingResponse] = []
    certifications: List[WorkerCertificationResponse] = []
    ppes: List[WorkerPPEResponse] = []
    authorizations: List[WorkerAuthorizationResponse] = []
    insurances: List[WorkerInsuranceResponse] = []
    leaves: List[WorkerLeaveResponse] = []
    passes: List[WorkerPassResponse] = []
    documents: List[WorkerDocumentResponse] = []
    inductions: List[WorkerInductionResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerDashboardStats(BaseModel):
    total_workers: int
    active_workers: int
    inactive_workers: int
    suspended_workers: int
    unauthorized_workers: int
    workers_pending_training: int
    expired_certifications_count: int
    ppe_compliance_percent: float
    authorization_compliance_percent: float


class WorkerReportsSummary(BaseModel):
    total_attendances_today: int
    present_today_count: int
    absent_today_count: int
    total_active_certifications: int
    expiring_certifications_30d: int
    total_trainings_completed: int
    pending_trainings_count: int
    compliant_ppe_items_count: int
    replacement_needed_ppe_count: int
    active_permits_count: int
    revoked_permits_count: int

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
    attendances: List[WorkerAttendanceResponse] = []
    trainings: List[WorkerTrainingResponse] = []
    certifications: List[WorkerCertificationResponse] = []
    ppes: List[WorkerPPEResponse] = []
    authorizations: List[WorkerAuthorizationResponse] = []
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

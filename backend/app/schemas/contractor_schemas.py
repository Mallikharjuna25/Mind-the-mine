"""
Contractor Management Pydantic Schemas (Module 3 -> Task 1)
Defines validation schemas for Contractor Registry, Contracts, Documents, Compliance & Performance.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class ContractorCreate(BaseModel):
    mine_id: str
    company_name: str = Field(..., min_length=2, max_length=255)
    registration_number: str = Field(..., min_length=3, max_length=100)
    contact_person: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(..., min_length=5, max_length=50)
    address: Optional[str] = None
    work_scope: str = Field(..., min_length=2, max_length=255)
    status: str = Field(default="ACTIVE")


class ContractorUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    work_scope: Optional[str] = None
    status: Optional[str] = None


class ContractCreate(BaseModel):
    mine_id: str
    contract_number: str = Field(..., min_length=3, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    contract_type: str = Field(..., description="MANPOWER, EQUIPMENT_LEASE, O&M, TRANSPORT")
    start_date: date
    end_date: date
    contract_value: float = Field(..., gt=0)
    status: str = Field(default="ACTIVE")


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    contract_type: Optional[str] = None
    end_date: Optional[date] = None
    contract_value: Optional[float] = None
    status: Optional[str] = None


class ContractRenewalRequest(BaseModel):
    new_end_date: date
    revised_value: Optional[float] = None
    remarks: Optional[str] = None


class ContractDocumentResponse(BaseModel):
    id: str
    contractor_id: str
    contract_id: Optional[str] = None
    document_type: str
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    uploaded_by_user_id: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractComplianceCreate(BaseModel):
    compliance_item: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., description="STATUTORY, SAFETY, ENVIRONMENTAL, LABOUR")
    status: str = Field(default="COMPLIANT", description="COMPLIANT, NON_COMPLIANT, PENDING_REVIEW")
    score_deduction: float = Field(default=0.0, ge=0.0, le=100.0)
    remarks: Optional[str] = None


class ContractComplianceResponse(BaseModel):
    id: str
    contractor_id: str
    compliance_item: str
    category: str
    status: str
    score_deduction: float
    remarks: Optional[str] = None
    inspected_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractPerformanceCreate(BaseModel):
    contract_id: Optional[str] = None
    rating: float = Field(..., ge=1.0, le=5.0)
    period: str = Field(..., description="e.g. 2026-Q1, 2026-M09")
    evaluated_by: str = Field(..., min_length=2, max_length=100)
    sla_adherence_percent: float = Field(default=100.0, ge=0.0, le=100.0)
    safety_incident_count: int = Field(default=0, ge=0)
    remarks: Optional[str] = None


class ContractPerformanceResponse(BaseModel):
    id: str
    contractor_id: str
    contract_id: Optional[str] = None
    rating: float
    period: str
    evaluated_by: str
    sla_adherence_percent: float
    safety_incident_count: int
    remarks: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractResponse(BaseModel):
    id: str
    contractor_id: str
    mine_id: str
    contract_number: str
    title: str
    contract_type: str
    start_date: date
    end_date: date
    contract_value: float
    status: str
    renewal_count: int
    documents: List[ContractDocumentResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractorResponse(BaseModel):
    id: str
    mine_id: str
    company_name: str
    registration_number: str
    contact_person: str
    email: str
    phone: str
    address: Optional[str] = None
    work_scope: str
    status: str
    compliance_score: float
    compliance_status: str
    performance_score: float
    contracts: List[ContractResponse] = []
    documents: List[ContractDocumentResponse] = []
    compliances: List[ContractComplianceResponse] = []
    performances: List[ContractPerformanceResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractorDashboardStats(BaseModel):
    total_contractors: int
    active_contractors: int
    suspended_contractors: int
    total_active_contracts: int
    total_contract_value: float
    expiring_contracts_count: int
    average_compliance_score: float
    non_compliant_contractors_count: int
    average_performance_rating: float

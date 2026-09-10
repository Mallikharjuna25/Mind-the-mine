from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class GrievanceBase(BaseModel):
    mine_id: str
    contractor_id: Optional[str] = None
    worker_id: Optional[str] = None
    complainant_name: str
    complainant_contact: str
    category: str
    title: str
    description: str
    priority: str = "MEDIUM"

class GrievanceCreate(GrievanceBase):
    pass

class GrievanceUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    assigned_to_role: Optional[str] = None

class GrievanceResolutionCreate(BaseModel):
    resolution_action: str
    resolution_notes: Optional[str] = None
    resolved_by_user_id: Optional[str] = None

class GrievanceResolutionResponse(BaseModel):
    id: str
    grievance_id: str
    resolution_action: str
    resolution_notes: Optional[str]
    resolved_by_user_id: Optional[str]
    resolved_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class GrievanceEvidenceResponse(BaseModel):
    id: str
    file_name: str
    file_path: str
    mime_type: str
    uploaded_by_user_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GrievanceResponse(GrievanceBase):
    id: str
    status: str
    assigned_to_user_id: Optional[str]
    assigned_to_role: Optional[str]
    sla_deadline: datetime
    is_escalated: bool
    created_at: datetime
    updated_at: datetime
    
    evidences: Optional[List[GrievanceEvidenceResponse]] = None
    resolutions: Optional[List[GrievanceResolutionResponse]] = None
    
    class Config:
        from_attributes = True

class ApprovalHistoryResponse(BaseModel):
    id: str
    actor_user_id: Optional[str]
    action: str
    previous_status: str
    new_status: str
    remarks: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ApprovalRequestBase(BaseModel):
    mine_id: str
    approval_type: str
    title: str
    entity_type: str
    entity_id: str
    requester_id: Optional[str] = None
    approver_role: str = "MINE_MANAGER"
    remarks: Optional[str] = None

class ApprovalRequestCreate(ApprovalRequestBase):
    pass

class ApprovalAction(BaseModel):
    action: str # APPROVE, REJECT, UNDER_REVIEW
    remarks: Optional[str] = None

class ApprovalRequestResponse(ApprovalRequestBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    histories: Optional[List[ApprovalHistoryResponse]] = None
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_grievances: int
    open_grievances: int
    resolved_grievances: int
    escalated_grievances: int
    pending_approvals: int
    approval_rate_percentage: float

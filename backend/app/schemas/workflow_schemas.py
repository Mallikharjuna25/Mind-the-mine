"""
Alerts, Corrective Actions & Escalation Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    violation_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    reading_id: Optional[str] = None
    title: str
    message: str
    alert_type: str
    severity: str
    channel: str
    target_role: str
    status: str
    sent_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by_user_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CorrectiveActionCreate(BaseModel):
    mine_id: str
    violation_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    title: str
    description: str
    assigned_to_user_id: Optional[str] = None
    assigned_to_contractor: Optional[str] = None
    priority: str = "HIGH"
    deadline: datetime


class CorrectiveActionVerifyRequest(BaseModel):
    status: str = Field(description="'RESOLVED', 'CLOSED', or 'REJECTED'")
    remediation_notes: Optional[str] = None
    proof_files_json: Optional[List[str]] = None


class CorrectiveActionResponse(BaseModel):
    id: str
    mine_id: str
    violation_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    action_code: str
    title: str
    description: str
    assigned_to_user_id: Optional[str] = None
    assigned_to_contractor: Optional[str] = None
    priority: str
    deadline: datetime
    status: str
    remediation_notes: Optional[str] = None
    proof_files_json: Optional[List[str]] = None
    closed_at: Optional[datetime] = None
    closed_by_user_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EscalationResponse(BaseModel):
    id: str
    alert_id: Optional[str] = None
    corrective_action_id: Optional[str] = None
    level: int
    escalated_from_role: str
    escalated_to_role: str
    reason: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}

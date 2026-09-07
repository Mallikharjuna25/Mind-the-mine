"""
Compliance & Violation Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ViolationVerifyRequest(BaseModel):
    """
    Officer confirmation / rejection of a candidate violation.
    """
    decision: str = Field(description="'CONFIRMED' or 'REJECTED'")
    rejection_reason: Optional[str] = None
    rule_reference: Optional[str] = None
    adjusted_severity: Optional[str] = None  # LOW, MEDIUM, HIGH, CRITICAL


class ViolationResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    camera_id: Optional[str] = None
    detection_event_id: Optional[str] = None
    violation_code: str
    category: str
    rule_reference: str
    severity: str
    status: str
    confidence: float
    description: str
    evidence_snapshot_path: Optional[str] = None
    evidence_video_path: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    verified_by_user_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViolationFilterParams(BaseModel):
    mine_id: Optional[str] = None
    zone_id: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None

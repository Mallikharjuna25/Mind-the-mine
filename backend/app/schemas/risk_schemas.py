"""
Risk Engine & Anomaly Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class RiskScoreComputeRequest(BaseModel):
    zone_id: Optional[str] = Field(default=None, description="If empty, computes for all active zones")
    mine_id: str


class RiskScoreResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    calculated_at: datetime
    composite_score: float
    risk_band: str  # LOW, MODERATE, HIGH, CRITICAL
    violation_subscore: float
    environment_subscore: float
    production_subscore: float
    equipment_subscore: float
    contributing_factors_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnomalyResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    anomaly_type: str
    title: str
    description: str
    severity: str
    metric_name: Optional[str] = None
    expected_value: Optional[float] = None
    observed_value: Optional[float] = None
    deviation_pct: Optional[float] = None
    is_resolved: bool
    resolved_by_user_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnomalyResolveRequest(BaseModel):
    resolution_note: str = Field(min_length=5)

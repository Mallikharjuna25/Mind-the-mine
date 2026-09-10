"""
Production Records Pydantic Schemas
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class ProductionRecordCreate(BaseModel):
    mine_id: str
    zone_id: str
    shift_date: date
    shift_number: int = Field(default=1, ge=1, le=3)
    seam_name: str = "Main Seam"
    target_tonnes: float = Field(ge=0.0)
    actual_tonnes: float = Field(ge=0.0)
    overburden_cbm: float = 0.0
    machinery_trips: int = 0
    downtime_minutes: int = 0
    downtime_reason: Optional[str] = None


class ProductionRecordResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    shift_date: date
    shift_number: int
    seam_name: str
    target_tonnes: float
    actual_tonnes: float
    overburden_cbm: float
    machinery_trips: int
    downtime_minutes: int
    downtime_reason: Optional[str] = None
    variance_pct: float
    logged_by_user_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

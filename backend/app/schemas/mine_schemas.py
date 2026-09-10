"""
Mine & Zone Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class MineZoneCreate(BaseModel):
    zone_code: str
    name: str
    zone_type: str
    polygon_geojson: Optional[Dict[str, Any]] = None
    risk_weight: float = Field(default=1.0, ge=0.5, le=3.0)
    is_restricted: bool = False


class MineZoneResponse(BaseModel):
    id: str
    mine_id: str
    zone_code: str
    name: str
    zone_type: str
    polygon_geojson: Optional[Dict[str, Any]] = None
    risk_weight: float
    is_restricted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MineCreate(BaseModel):
    mine_code: str
    name: str
    subsidiary: str
    state: str
    district: str
    latitude: float
    longitude: float
    area_sqkm: float = 12.5
    lease_boundary_geojson: Optional[Dict[str, Any]] = None


class MineResponse(BaseModel):
    id: str
    mine_code: str
    name: str
    subsidiary: str
    state: str
    district: str
    latitude: float
    longitude: float
    area_sqkm: float
    lease_boundary_geojson: Optional[Dict[str, Any]] = None
    is_active: bool
    zones: Optional[List[MineZoneResponse]] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}

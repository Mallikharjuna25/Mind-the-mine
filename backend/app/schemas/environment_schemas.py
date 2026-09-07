"""
Environmental Telemetry Pydantic Schemas
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EnvironmentalReadingCreate(BaseModel):
    mine_id: str
    zone_id: str
    sensor_code: str
    reading_timestamp: Optional[datetime] = None
    methane_ch4_pct: Optional[float] = Field(default=None, description="Methane gas percentage")
    carbon_monoxide_co_ppm: Optional[float] = Field(default=None, description="CO parts per million")
    oxygen_o2_pct: Optional[float] = Field(default=None, description="Oxygen percentage")
    dust_pm25: Optional[float] = None
    dust_pm10: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    noise_db: Optional[float] = None
    source: str = "IOT_SENSOR"


class EnvironmentalReadingResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    sensor_code: str
    reading_timestamp: datetime
    methane_ch4_pct: Optional[float] = None
    carbon_monoxide_co_ppm: Optional[float] = None
    oxygen_o2_pct: Optional[float] = None
    dust_pm25: Optional[float] = None
    dust_pm10: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    noise_db: Optional[float] = None
    air_quality_index: Optional[float] = None
    is_breach: bool
    breach_details_json: Optional[Dict[str, Any]] = None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}

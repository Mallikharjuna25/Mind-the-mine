"""
CCTV Camera & Detection Event Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class CameraCreate(BaseModel):
    mine_id: str
    zone_id: str
    camera_code: str
    name: str
    rtsp_stream_url: Optional[str] = None
    ip_address: Optional[str] = None
    location_desc: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolution: str = "1080p"
    fps: float = 25.0
    coverage_angle: float = 90.0
    ppe_check_enabled: bool = True
    restricted_zone_enabled: bool = True
    fire_smoke_enabled: bool = True


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    rtsp_stream_url: Optional[str] = None
    ppe_check_enabled: Optional[bool] = None
    restricted_zone_enabled: Optional[bool] = None
    fire_smoke_enabled: Optional[bool] = None


class CameraResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    camera_code: str
    name: str
    rtsp_stream_url: Optional[str] = None
    ip_address: Optional[str] = None
    location_desc: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    resolution: str
    fps: float
    coverage_angle: float
    ppe_check_enabled: bool
    restricted_zone_enabled: bool
    fire_smoke_enabled: bool
    last_heartbeat_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DetectionIngestRequest(BaseModel):
    """
    Payload posted by the vision inference pipeline when an object or anomaly is spotted.
    """
    camera_id: str
    detection_type: str  # PPE_VIOLATION, RESTRICTED_ZONE_INTRUSION, FIRE_SMOKE, VEHICLE_HAZARD
    raw_class_name: str  # e.g., 'no_helmet', 'no_vest', 'smoke'
    confidence_score: float = Field(ge=0.0, le=1.0)
    bounding_box_json: Optional[Dict[str, Any]] = None  # {"x_min": 0.2, "y_min": 0.1, "x_max": 0.4, "y_max": 0.5}
    snapshot_base64: Optional[str] = None  # Base64 snapshot if available
    metadata: Optional[Dict[str, Any]] = None


class DetectionEventResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    camera_id: str
    detection_type: str
    raw_class_name: str
    confidence_score: float
    bounding_box_json: Optional[Dict[str, Any]] = None
    snapshot_image_path: Optional[str] = None
    frame_timestamp: datetime
    promoted_to_violation: bool
    violation_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

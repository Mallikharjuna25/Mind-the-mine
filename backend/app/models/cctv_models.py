"""
CCTV Camera Registry & Detection Event Models
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class CameraRegistry(BaseModelMixin):
    __tablename__ = "camera_registry"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    camera_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    rtsp_stream_url = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    location_desc = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE, ERROR
    resolution = Column(String(20), default="1080p", nullable=False)
    fps = Column(Float, default=25.0, nullable=False)
    coverage_angle = Column(Float, default=90.0, nullable=False)
    
    # Feature Toggles
    ppe_check_enabled = Column(Boolean, default=True, nullable=False)
    restricted_zone_enabled = Column(Boolean, default=True, nullable=False)
    fire_smoke_enabled = Column(Boolean, default=True, nullable=False)
    
    last_heartbeat_at = Column(DateTime, default=utc_now, nullable=False)

    mine = relationship("Mine", back_populates="cameras")
    zone = relationship("MineZone", back_populates="cameras")
    detections = relationship("DetectionEvent", back_populates="camera", cascade="all, delete-orphan")


class DetectionEvent(BaseModelMixin):
    __tablename__ = "detection_events"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(String(36), ForeignKey("camera_registry.id", ondelete="CASCADE"), nullable=False, index=True)
    
    detection_type = Column(String(50), nullable=False, index=True)  # PPE_VIOLATION, RESTRICTED_ZONE_INTRUSION, FIRE_SMOKE, VEHICLE_HAZARD
    raw_class_name = Column(String(100), nullable=False)  # e.g., 'no_helmet', 'no_vest', 'person_in_restricted_zone', 'smoke'
    confidence_score = Column(Float, nullable=False)
    
    # Normalized bounding box [x_min, y_min, x_max, y_max] or list of boxes
    bounding_box_json = Column(JSON, nullable=True)
    snapshot_image_path = Column(String(500), nullable=True)
    frame_timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    
    # Promotion Status
    promoted_to_violation = Column(Boolean, default=False, nullable=False)
    violation_id = Column(String(36), nullable=True)  # Populated when candidate violation created

    camera = relationship("CameraRegistry", back_populates="detections")

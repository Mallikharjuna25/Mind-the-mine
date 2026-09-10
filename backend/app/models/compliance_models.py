"""
Statutory Compliance & Violation Models
Enforces Human-in-the-Loop AI Governance: AI generates CANDIDATE violations;
officers verify/confirm or reject with statutory citations.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class Violation(BaseModelMixin):
    __tablename__ = "violations"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(String(36), ForeignKey("camera_registry.id", ondelete="SET NULL"), nullable=True, index=True)
    detection_event_id = Column(String(36), ForeignKey("detection_events.id", ondelete="SET NULL"), nullable=True, index=True)
    
    violation_code = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # PPE, RESTRICTED_ZONE, FIRE_SMOKE, EQUIPMENT, ENVIRONMENTAL, LABOUR, PRODUCTION
    rule_reference = Column(String(255), nullable=False)  # e.g., "CMR 2017 Reg 130", "DGMS Tech Circular 04/2023"
    
    severity = Column(String(20), default="MEDIUM", nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="CANDIDATE", nullable=False, index=True)  # CANDIDATE, CONFIRMED, REJECTED, RESOLVED, CLOSED
    
    confidence = Column(Float, nullable=False)
    description = Column(String(1000), nullable=False)
    evidence_snapshot_path = Column(String(500), nullable=True)
    evidence_video_path = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    # Verification Fields
    verified_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(500), nullable=True)

    # Relationships
    mine = relationship("Mine", back_populates="violations")
    zone = relationship("MineZone", back_populates="violations")
    corrective_actions = relationship("CorrectiveAction", back_populates="violation", cascade="all, delete-orphan")

"""
Risk Engine & Anomaly Detection Database Models
Implements explainable risk scoring and recurring pattern identification.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class RiskScore(BaseModelMixin):
    __tablename__ = "risk_scores"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    calculated_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    composite_score = Column(Float, nullable=False)  # 0.0 to 100.0 (Higher = Greater Risk)
    risk_band = Column(String(20), nullable=False, index=True)  # LOW (0-25), MODERATE (26-50), HIGH (51-75), CRITICAL (76-100)
    
    # Explainable sub-indices
    violation_subscore = Column(Float, default=0.0, nullable=False)
    environment_subscore = Column(Float, default=0.0, nullable=False)
    production_subscore = Column(Float, default=0.0, nullable=False)
    equipment_subscore = Column(Float, default=0.0, nullable=False)
    
    contributing_factors_json = Column(JSON, nullable=True)  # Top contributing risk drivers

    mine = relationship("Mine", back_populates="risk_scores")
    zone = relationship("MineZone", back_populates="risk_scores")


class Anomaly(BaseModelMixin):
    __tablename__ = "anomalies"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    anomaly_type = Column(String(50), nullable=False, index=True)  # RECURRING_VIOLATION, PRODUCTION_ANOMALY, SENSOR_DRIFT, EQUIPMENT_BREAKDOWN_PATTERN
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    severity = Column(String(20), default="HIGH", nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    metric_name = Column(String(100), nullable=True)
    expected_value = Column(Float, nullable=True)
    observed_value = Column(Float, nullable=True)
    deviation_pct = Column(Float, nullable=True)
    
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_note = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)

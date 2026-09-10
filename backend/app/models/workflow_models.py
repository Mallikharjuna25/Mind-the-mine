"""
Alerts, Corrective Action Remediation & SLA Escalation Models
Automates response loops: Safety Breach -> Alert Dispatch -> Corrective Action -> 3-Tier Escalation.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class Alert(BaseModelMixin):
    __tablename__ = "alerts"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    violation_id = Column(String(36), ForeignKey("violations.id", ondelete="SET NULL"), nullable=True, index=True)
    anomaly_id = Column(String(36), ForeignKey("anomalies.id", ondelete="SET NULL"), nullable=True, index=True)
    reading_id = Column(String(36), ForeignKey("environmental_readings.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    alert_type = Column(String(50), nullable=False, index=True)  # SAFETY_BREACH, GAS_ALARM, EXPIRY_WARNING, ANOMALY_DETECTED, PRODUCTION_DROP
    severity = Column(String(20), default="HIGH", nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    channel = Column(String(30), default="IN_APP", nullable=False)  # IN_APP, SMS, EMAIL, WEBHOOK, SIREN
    target_role = Column(String(50), default="SAFETY_OFFICER", nullable=False)  # Role to receive alert
    
    status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, SENT, ACKNOWLEDGED, ESCALATED
    sent_at = Column(DateTime, default=utc_now, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    escalations = relationship("Escalation", back_populates="alert", cascade="all, delete-orphan")


class CorrectiveAction(BaseModelMixin):
    __tablename__ = "corrective_actions"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    violation_id = Column(String(36), ForeignKey("violations.id", ondelete="CASCADE"), nullable=True, index=True)
    anomaly_id = Column(String(36), ForeignKey("anomalies.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    
    assigned_to_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to_contractor = Column(String(255), nullable=True)
    
    priority = Column(String(20), default="HIGH", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    deadline = Column(DateTime, nullable=False)
    
    status = Column(String(30), default="OPEN", nullable=False, index=True)  # OPEN, IN_PROGRESS, PENDING_VERIFICATION, RESOLVED, CLOSED
    remediation_notes = Column(String(1000), nullable=True)
    proof_files_json = Column(JSON, nullable=True)  # Array of uploaded photos/docs proving remediation
    
    closed_at = Column(DateTime, nullable=True)
    closed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    violation = relationship("Violation", back_populates="corrective_actions")
    escalations = relationship("Escalation", back_populates="corrective_action", cascade="all, delete-orphan")


class Escalation(BaseModelMixin):
    __tablename__ = "escalations"

    alert_id = Column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=True, index=True)
    corrective_action_id = Column(String(36), ForeignKey("corrective_actions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    level = Column(Integer, default=1, nullable=False)  # Level 1 (Safety Officer), Level 2 (Mine Manager), Level 3 (Corporate / DGMS)
    escalated_from_role = Column(String(50), nullable=False)
    escalated_to_role = Column(String(50), nullable=False)
    
    reason = Column(String(500), nullable=False)
    triggered_at = Column(DateTime, default=utc_now, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)

    alert = relationship("Alert", back_populates="escalations")
    corrective_action = relationship("CorrectiveAction", back_populates="escalations")

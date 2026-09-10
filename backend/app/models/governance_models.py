from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin

class Grievance(BaseModelMixin):
    __tablename__ = "grievances"

    mine_id = Column(String(36), nullable=False)
    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True)
    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    complainant_name = Column(String(255), nullable=False)
    complainant_contact = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False) # SAFETY, WAGE_DISPUTE, HARASSMENT, WORKING_CONDITIONS, CONTRACTOR_SLA
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="OPEN") # OPEN, ASSIGNED, UNDER_REVIEW, ESCALATED, RESOLVED, CLOSED
    assigned_to_user_id = Column(String(36), nullable=True)
    assigned_to_role = Column(String(50), default="SAFETY_OFFICER")
    sla_deadline = Column(DateTime, nullable=False)
    is_escalated = Column(Boolean, default=False)

    evidences = relationship("GrievanceEvidence", back_populates="grievance", cascade="all, delete-orphan", lazy="selectin")
    resolutions = relationship("GrievanceResolution", back_populates="grievance", cascade="all, delete-orphan", lazy="selectin")

class GrievanceEvidence(BaseModelMixin):
    __tablename__ = "grievance_evidences"

    grievance_id = Column(String(36), ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    uploaded_by_user_id = Column(String(36), nullable=True)

    grievance = relationship("Grievance", back_populates="evidences")

class GrievanceResolution(BaseModelMixin):
    __tablename__ = "grievance_resolutions"

    grievance_id = Column(String(36), ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False)
    resolution_action = Column(Text, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_by_user_id = Column(String(36), nullable=True)
    resolved_at = Column(DateTime, nullable=False)

    grievance = relationship("Grievance", back_populates="resolutions")

class ApprovalRequest(BaseModelMixin):
    __tablename__ = "approval_requests"

    mine_id = Column(String(36), nullable=False)
    approval_type = Column(String(50), nullable=False) # CONTRACTOR_APPROVAL, CONTRACT_RENEWAL, WORKER_AUTHORIZATION, COMPLIANCE_APPROVAL, TRAINING_APPROVAL, GOVERNANCE_ACTION
    title = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False) # Contractor, Contract, Worker, Compliance, Training
    entity_id = Column(String(36), nullable=False)
    requester_id = Column(String(36), nullable=True)
    approver_role = Column(String(50), default="MINE_MANAGER")
    status = Column(String(30), default="PENDING") # PENDING, UNDER_REVIEW, APPROVED, REJECTED, CANCELLED
    remarks = Column(Text, nullable=True)

    histories = relationship("ApprovalHistory", back_populates="approval_request", cascade="all, delete-orphan", lazy="selectin")

class ApprovalHistory(BaseModelMixin):
    __tablename__ = "approval_histories"

    approval_request_id = Column(String(36), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False)
    actor_user_id = Column(String(36), nullable=True)
    action = Column(String(50), nullable=False) # SUBMITTED, REVIEWED, APPROVED, REJECTED, CANCELLED
    previous_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    remarks = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    approval_request = relationship("ApprovalRequest", back_populates="histories")

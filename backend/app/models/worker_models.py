"""
Worker & Compliance Management Models (Module 3 -> Task 2)
Defines Worker, WorkerAttendance, WorkerTraining, WorkerCertification, WorkerPPE, and WorkerAuthorization.
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Float, JSON, Date, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class Worker(BaseModelMixin):
    __tablename__ = "workers"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True, index=True)
    
    employee_id = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)  # EXCAVATION, UNDERGROUND_OPS, TRANSPORT, MAINTENANCE, SAFETY
    role = Column(String(100), nullable=False)  # HEAVY_EQUIPMENT_OPERATOR, MINER, BLASTER, FITTER, ELECTRICIAN, INSPECTOR
    
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=False)
    emergency_contact_name = Column(String(100), nullable=False)
    emergency_contact_phone = Column(String(50), nullable=False)
    
    joining_date = Column(Date, nullable=False)
    status = Column(String(30), default="ACTIVE", nullable=False, index=True)  # ACTIVE, INACTIVE, SUSPENDED, UNAUTHORIZED

    # Relationships
    mine = relationship("Mine", backref="workers", lazy="selectin")
    contractor = relationship("Contractor", backref="workers", lazy="selectin")
    attendances = relationship("WorkerAttendance", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    trainings = relationship("WorkerTraining", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    certifications = relationship("WorkerCertification", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    ppes = relationship("WorkerPPE", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    authorizations = relationship("WorkerAuthorization", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")


class WorkerAttendance(BaseModelMixin):
    __tablename__ = "worker_attendances"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    
    shift = Column(String(30), nullable=False)  # MORNING, AFTERNOON, NIGHT
    check_in = Column(DateTime, default=utc_now, nullable=False)
    check_out = Column(DateTime, nullable=True)
    status = Column(String(30), default="PRESENT", nullable=False, index=True)  # PRESENT, ABSENT, LATE, LEAVE, OVERTIME

    # Relationships
    worker = relationship("Worker", back_populates="attendances")


class WorkerTraining(BaseModelMixin):
    __tablename__ = "worker_trainings"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    program_name = Column(String(255), nullable=False)
    trainer_name = Column(String(100), nullable=False)
    completed_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="COMPLETED", nullable=False, index=True)  # COMPLETED, PENDING, EXPIRED

    # Relationships
    worker = relationship("Worker", back_populates="trainings")


class WorkerCertification(BaseModelMixin):
    __tablename__ = "worker_certifications"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    certificate_name = Column(String(255), nullable=False)
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)
    issuing_authority = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)
    valid_from = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    verification_status = Column(String(30), default="VERIFIED", nullable=False, index=True)  # VERIFIED, PENDING, EXPIRED

    # Relationships
    worker = relationship("Worker", back_populates="certifications")


class WorkerPPE(BaseModelMixin):
    __tablename__ = "worker_ppes"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    item_type = Column(String(50), nullable=False)  # HELMET, HIGH_VIS_VEST, SAFETY_BOOTS, RESPIRATOR, HARNESS, GOGGLES
    issuance_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    compliance_status = Column(String(30), default="COMPLIANT", nullable=False, index=True)  # COMPLIANT, EXPIRED, PENDING_ISSUANCE, REPLACEMENT_REQUIRED
    remarks = Column(Text, nullable=True)

    # Relationships
    worker = relationship("Worker", back_populates="ppes")


class WorkerAuthorization(BaseModelMixin):
    __tablename__ = "worker_authorizations"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    zone_id = Column(String(100), nullable=False, index=True)  # Restricted Zone Name / ID
    permit_type = Column(String(50), nullable=False)  # HOT_WORK, UNDERGROUND_ENTRY, CONFINED_SPACE, HIGH_VOLTAGE
    grant_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="GRANTED", nullable=False, index=True)  # GRANTED, REVOKED, EXPIRED
    granted_by = Column(String(100), nullable=False)

    # Relationships
    worker = relationship("Worker", back_populates="authorizations")

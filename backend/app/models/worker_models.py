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
    
    blood_group = Column(String(10), default="O+", nullable=True)
    rfid_tag = Column(String(50), nullable=True, index=True)
    medical_fitness_status = Column(String(30), default="FIT", nullable=False)  # FIT, TEMPORARILY_UNFIT, PERMANENTLY_UNFIT
    medical_exam_date = Column(Date, nullable=True)
    medical_expiry_date = Column(Date, nullable=True)

    # Relationships
    mine = relationship("Mine", backref="workers", lazy="selectin")
    contractor = relationship("Contractor", backref="workers", lazy="selectin")
    attendances = relationship("WorkerAttendance", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    trainings = relationship("WorkerTraining", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    certifications = relationship("WorkerCertification", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    ppes = relationship("WorkerPPE", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    authorizations = relationship("WorkerAuthorization", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    insurances = relationship("WorkerInsurance", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    leaves = relationship("WorkerLeave", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    passes = relationship("WorkerPass", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    documents = relationship("WorkerDocument", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")
    inductions = relationship("WorkerInduction", back_populates="worker", cascade="all, delete-orphan", lazy="selectin")


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


class WorkerInsurance(BaseModelMixin):
    __tablename__ = "worker_insurances"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_provider = Column(String(255), nullable=False)  # e.g. "LIC Group Coal Mine Scheme", "New India Assurance"
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    policy_type = Column(String(100), nullable=False)  # ACCIDENTAL_DEATH_DISABILITY, CRITICAL_ILLNESS, CMPF_PROVIDENT_FUND
    coverage_amount = Column(Float, nullable=False)  # e.g. 1500000.0
    start_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    nominee_name = Column(String(100), nullable=False)
    nominee_relation = Column(String(50), nullable=False)  # SPOUSE, CHILD, PARENT
    premium_status = Column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, EXPIRED, PENDING_RENEWAL
    tpa_contact_number = Column(String(50), nullable=True)

    worker = relationship("Worker", back_populates="insurances")


class WorkerLeave(BaseModelMixin):
    __tablename__ = "worker_leaves"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False)  # CASUAL, SICK_MEDICAL, PRIVILEGE_EARNED, GATE_PASS_SHIFT_EXIT
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Float, nullable=False, default=1.0)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    approved_by = Column(String(100), nullable=True)
    supervisor_remarks = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="leaves")


class WorkerPass(BaseModelMixin):
    __tablename__ = "worker_passes"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)

    rfid_uid = Column(String(100), nullable=False, index=True)
    pass_number = Column(String(100), unique=True, nullable=False, index=True)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="ACTIVE", nullable=False, index=True)  # ACTIVE, EXPIRED, REVOKED, BLOCKED, PENDING
    access_level = Column(String(50), default="GENERAL_SURFACE", nullable=False)  # GENERAL_SURFACE, HAUL_ROAD, DEEP_PIT, UNDERGROUND, BLASTING_ZONE
    permitted_zones = Column(JSON, default=list, nullable=False)  # List of zone strings e.g. ["PIT-01", "HAUL-02"]
    last_seen = Column(DateTime, nullable=True)
    issued_by = Column(String(100), nullable=False)
    revoked_by = Column(String(100), nullable=True)
    revocation_reason = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="passes")
    mine = relationship("Mine", lazy="selectin")


class WorkerDocument(BaseModelMixin):
    __tablename__ = "worker_documents"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=True, index=True)
    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=True, index=True)

    document_type = Column(String(50), nullable=False, index=True)  # IDENTITY_CARD, FITNESS_CERTIFICATE_FORM_O_P, DGMS_VOCATIONAL_TRAINING, BLASTING_COMPETENCY, CONTRACTOR_AUTHORIZATION, HEMM_DRIVING_LICENSE
    document_number = Column(String(100), nullable=True, index=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)

    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)

    ocr_status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, AUTO_ACCEPTED, NEEDS_REVIEW, VERIFIED, REJECTED
    ocr_confidence = Column(Float, default=0.0, nullable=False)
    raw_ocr_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    validation_errors = Column(JSON, nullable=True)

    verification_status = Column(String(30), default="PENDING", nullable=False, index=True)  # VERIFIED, PENDING, REJECTED
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="documents")
    contractor = relationship("Contractor", backref="workforce_documents", lazy="selectin")


class WorkerInduction(BaseModelMixin):
    __tablename__ = "worker_inductions"

    worker_id = Column(String(36), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)

    induction_type = Column(String(50), default="INITIAL_STATUTORY", nullable=False)  # INITIAL_STATUTORY, REFRESHER_ANNUAL, SPECIALIZED_ZONE, POST_INCIDENT
    training_title = Column(String(255), nullable=False)
    trainer_name = Column(String(100), nullable=False)
    training_date = Column(Date, nullable=False)
    validity_months = Column(Integer, default=12, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    score_percent = Column(Float, nullable=True)

    certificate_document_id = Column(String(36), ForeignKey("worker_documents.id", ondelete="SET NULL"), nullable=True)
    verification_status = Column(String(30), default="VERIFIED", nullable=False, index=True)  # VERIFIED, PENDING, REJECTED
    status = Column(String(30), default="COMPLETED", nullable=False, index=True)  # PENDING, SCHEDULED, COMPLETED, EXPIRED, FAILED, REQUIRES_RENEWAL
    remarks = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="inductions")
    mine = relationship("Mine", lazy="selectin")
    certificate_document = relationship("WorkerDocument", lazy="selectin")

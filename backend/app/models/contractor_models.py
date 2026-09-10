"""
Contractor Management Models (Module 3 -> Task 1)
Defines Contractor, Contract, ContractDocument, ContractCompliance, and ContractPerformance.
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Float, JSON, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class Contractor(BaseModelMixin):
    __tablename__ = "contractors"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    registration_number = Column(String(100), unique=True, nullable=False, index=True)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=True)
    work_scope = Column(String(255), nullable=False)  # e.g., EXCAVATION, TRANSPORT, MAINTENANCE, DRILLING
    
    status = Column(String(30), default="ACTIVE", nullable=False, index=True)  # ACTIVE, SUSPENDED, TERMINATED, EXPIRED
    compliance_score = Column(Float, default=100.0, nullable=False)
    compliance_status = Column(String(30), default="COMPLIANT", nullable=False, index=True)  # COMPLIANT, WARNING, NON_COMPLIANT
    performance_score = Column(Float, default=5.0, nullable=False)  # Rating out of 5.0

    # Relationships
    mine = relationship("Mine", backref="contractors", lazy="selectin")
    contracts = relationship("Contract", back_populates="contractor", cascade="all, delete-orphan", lazy="selectin")
    documents = relationship("ContractDocument", back_populates="contractor", cascade="all, delete-orphan", lazy="selectin")
    compliances = relationship("ContractCompliance", back_populates="contractor", cascade="all, delete-orphan", lazy="selectin")
    performances = relationship("ContractPerformance", back_populates="contractor", cascade="all, delete-orphan", lazy="selectin")


class Contract(BaseModelMixin):
    __tablename__ = "contracts"

    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(50), nullable=False)  # MANPOWER, EQUIPMENT_LEASE, O&M, TRANSPORT
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False, index=True)
    contract_value = Column(Float, nullable=False)
    
    status = Column(String(30), default="ACTIVE", nullable=False, index=True)  # DRAFT, ACTIVE, EXPIRING_SOON, EXPIRED, RENEWED, TERMINATED
    renewal_count = Column(Integer, default=0, nullable=False)

    # Relationships
    contractor = relationship("Contractor", back_populates="contracts")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan", lazy="selectin")
    performances = relationship("ContractPerformance", back_populates="contract", cascade="all, delete-orphan", lazy="selectin")


class ContractDocument(BaseModelMixin):
    __tablename__ = "contract_documents"

    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True, index=True)
    
    document_type = Column(String(50), nullable=False)  # WORK_ORDER, EPF_ESI_CERTIFICATE, SAFETY_POLICY, DGMS_CLEARANCE, INSURANCE
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True, index=True)

    # Relationships
    contractor = relationship("Contractor", back_populates="documents")
    contract = relationship("Contract", back_populates="documents")


class ContractCompliance(BaseModelMixin):
    __tablename__ = "contract_compliances"

    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    compliance_item = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # STATUTORY, SAFETY, ENVIRONMENTAL, LABOUR
    status = Column(String(30), default="COMPLIANT", nullable=False, index=True)  # COMPLIANT, NON_COMPLIANT, PENDING_REVIEW
    score_deduction = Column(Float, default=0.0, nullable=False)
    remarks = Column(Text, nullable=True)
    inspected_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    contractor = relationship("Contractor", back_populates="compliances")


class ContractPerformance(BaseModelMixin):
    __tablename__ = "contract_performances"

    contractor_id = Column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True, index=True)
    
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    period = Column(String(50), nullable=False)  # e.g., 2026-Q1, 2026-M09
    evaluated_by = Column(String(100), nullable=False)
    sla_adherence_percent = Column(Float, default=100.0, nullable=False)
    safety_incident_count = Column(Integer, default=0, nullable=False)
    remarks = Column(Text, nullable=True)

    # Relationships
    contractor = relationship("Contractor", back_populates="performances")
    contract = relationship("Contract", back_populates="performances")

"""
Equipment Asset Registry & OCR Document Models
Tracks Heavy Earth Moving Machinery (HEMM), electrical installations, fire extinguishers,
and automates statutory fitness certificate OCR digitization.
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Float, JSON, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class EquipmentAsset(BaseModelMixin):
    __tablename__ = "equipment_assets"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    asset_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    serial_number = Column(String(100), unique=True, nullable=False)
    make_model = Column(String(100), nullable=False)
    
    manufacture_date = Column(Date, nullable=True)
    purchase_date = Column(Date, nullable=True)
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    fitness_expiry_date = Column(Date, nullable=True, index=True)
    
    qr_code_data = Column(String(500), nullable=True)
    working_condition = Column(String(30), default="OPERATIONAL", nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    metadata_json = Column(JSON, nullable=True)

    mine = relationship("Mine", back_populates="equipment")
    zone = relationship("MineZone", back_populates="equipment")
    documents = relationship("EquipmentDocument", back_populates="asset", cascade="all, delete-orphan", lazy="selectin")


class EquipmentDocument(BaseModelMixin):
    __tablename__ = "equipment_documents"

    asset_id = Column(String(36), ForeignKey("equipment_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    ocr_extracted_text = Column(String, nullable=True)
    ocr_parsed_json = Column(JSON, nullable=True)
    ocr_confidence = Column(Float, default=0.0, nullable=False)
    
    verification_status = Column(String(30), default="EXTRACTED", nullable=False)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True, index=True)

    asset = relationship("EquipmentAsset", back_populates="documents")

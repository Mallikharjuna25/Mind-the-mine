"""
Equipment Asset & Document Pydantic Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    mine_id: str
    zone_id: str
    asset_code: str
    name: str
    category: str  # HEMM, EXCAVATOR, DUMPER, CONVEYOR, VENTILATION_FAN, SUBSTATION, FIRE_SAFETY
    serial_number: str
    make_model: str
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    fitness_expiry_date: Optional[date] = None
    working_condition: str = "OPERATIONAL"


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[str] = None
    working_condition: Optional[str] = None
    status: Optional[str] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    fitness_expiry_date: Optional[date] = None


class EquipmentDocumentResponse(BaseModel):
    id: str
    asset_id: str
    document_type: str
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    ocr_extracted_text: Optional[str] = None
    ocr_parsed_json: Optional[Dict[str, Any]] = None
    ocr_confidence: float
    verification_status: str
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetResponse(BaseModel):
    id: str
    mine_id: str
    zone_id: str
    asset_code: str
    name: str
    category: str
    serial_number: str
    make_model: str
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    fitness_expiry_date: Optional[date] = None
    qr_code_data: Optional[str] = None
    working_condition: str
    status: str
    documents: List[EquipmentDocumentResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}

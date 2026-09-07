"""
Equipment Asset Registry & OCR Document Upload Router
"""

import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.equipment_models import EquipmentAsset, EquipmentDocument
from app.schemas.equipment_schemas import AssetCreate, AssetUpdate, AssetResponse, EquipmentDocumentResponse
from app.schemas.common_schemas import ApiResponse
from app.services.equipment_service import equipment_service

router = APIRouter(prefix="/mine", tags=["Equipment Compliance & OCR"])
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/equipment", response_model=ApiResponse[AssetResponse])
async def create_equipment(
    payload: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("equipment.asset.create"))
):
    asset = await equipment_service.create_asset(db=db, payload=payload, user_id=current_user.sub)
    return ApiResponse(message="Equipment asset registered with QR code", data=AssetResponse.model_validate(asset))


@router.get("/equipment", response_model=ApiResponse[List[AssetResponse]])
async def list_equipment(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    condition: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(EquipmentAsset).options(selectinload(EquipmentAsset.documents))
    if mine_id:
        stmt = stmt.where(EquipmentAsset.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(EquipmentAsset.zone_id == zone_id)
    if category:
        stmt = stmt.where(EquipmentAsset.category == category)
    if condition:
        stmt = stmt.where(EquipmentAsset.working_condition == condition)

    res = await db.execute(stmt)
    assets = list(res.scalars().all())
    return ApiResponse(data=[AssetResponse.model_validate(a) for a in assets])


@router.get("/equipment/expiring", response_model=ApiResponse[List[AssetResponse]])
async def get_expiring_equipment(
    mine_id: str = Query(...),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    assets = await equipment_service.get_expiring_assets(db=db, mine_id=mine_id, days=days)
    return ApiResponse(message=f"Assets expiring within {days} days", data=[AssetResponse.model_validate(a) for a in assets])


@router.post("/equipment/{asset_id}/documents", response_model=ApiResponse[EquipmentDocumentResponse])
async def upload_equipment_document(
    asset_id: str,
    document_type: str = Form(default="DGMS_FITNESS_CERTIFICATE"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("equipment.document.upload"))
):
    """
    Uploads a statutory document and triggers the automated OCR text extraction & expiry update.
    """
    file_path = os.path.join(settings.UPLOAD_DIR, f"{asset_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    doc = await equipment_service.process_document_upload(
        db=db,
        asset_id=asset_id,
        document_type=document_type,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        user_id=current_user.sub
    )

    return ApiResponse(
        message=f"Document uploaded & OCR processed (Status: {doc.verification_status}, Confidence: {doc.ocr_confidence})",
        data=EquipmentDocumentResponse.model_validate(doc)
    )

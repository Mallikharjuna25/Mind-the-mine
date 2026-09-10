"""
Equipment Compliance & OCR Document Processing Service
Orchestrates Asset Lifecycle, QR Code tagging, and automated statutory certificate OCR extraction.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.core.config import settings
from app.core.exceptions import EntityNotFoundError
from app.core.logging_config import logger
from app.models.base import generate_uuid
from app.models.equipment_models import EquipmentAsset, EquipmentDocument
from app.models.workflow_models import Alert
from app.schemas.equipment_schemas import AssetCreate, AssetUpdate
from app.ai.ocr.ocr_engine import ocr_engine
from app.ai.ocr.certificate_parser import parse_date_safely
from app.services.audit_service import audit_service


class EquipmentService:

    @classmethod
    async def create_asset(cls, db: AsyncSession, payload: AssetCreate, user_id: Optional[str] = None) -> EquipmentAsset:
        qr_payload = json.dumps({
            "asset_code": payload.asset_code,
            "mine_id": payload.mine_id,
            "category": payload.category,
            "serial_no": payload.serial_number
        })

        asset = EquipmentAsset(
            id=generate_uuid(),
            mine_id=payload.mine_id,
            zone_id=payload.zone_id,
            asset_code=payload.asset_code,
            name=payload.name,
            category=payload.category,
            serial_number=payload.serial_number,
            make_model=payload.make_model,
            manufacture_date=payload.manufacture_date,
            purchase_date=payload.purchase_date,
            last_maintenance_date=payload.last_maintenance_date,
            next_maintenance_date=payload.next_maintenance_date,
            fitness_expiry_date=payload.fitness_expiry_date,
            qr_code_data=qr_payload,
            working_condition=payload.working_condition,
            status="ACTIVE"
        )
        db.add(asset)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="EQUIPMENT_ASSET_CREATED",
            entity_type="EquipmentAsset",
            entity_id=asset.id,
            changes={"asset_code": asset.asset_code, "name": asset.name},
            user_id=user_id,
            mine_id=payload.mine_id
        )
        await db.commit()
        await db.refresh(asset)
        return asset

    @classmethod
    async def process_document_upload(
        cls,
        db: AsyncSession,
        asset_id: str,
        document_type: str,
        file_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        user_id: Optional[str] = None
    ) -> EquipmentDocument:
        """
        Runs the 5-step OCR Extraction & Conditional Asset Expiry Update pipeline.
        """
        stmt = select(EquipmentAsset).where(EquipmentAsset.id == asset_id)
        res = await db.execute(stmt)
        asset = res.scalars().first()
        if not asset:
            raise EntityNotFoundError("EquipmentAsset", asset_id)

        # 1. Step 1 & 2: OCR Extraction + Field Parsing
        raw_text, parsed_json, confidence = ocr_engine.process_equipment_document(file_path)

        # 2. Step 3: Store Document Record
        valid_from = parse_date_safely(parsed_json.get("inspection_date", ""))
        valid_until = parse_date_safely(parsed_json.get("expiry_date", ""))

        doc = EquipmentDocument(
            id=generate_uuid(),
            asset_id=asset.id,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
            uploaded_by_user_id=user_id,
            ocr_extracted_text=raw_text,
            ocr_parsed_json=parsed_json,
            ocr_confidence=confidence,
            verification_status="EXTRACTED" if confidence >= settings.OCR_CONFIDENCE_THRESHOLD else "PENDING_REVIEW",
            valid_from=valid_from,
            valid_until=valid_until
        )
        db.add(doc)
        await db.flush()

        # 3. Step 4: Conditional Asset Update
        if confidence >= settings.OCR_CONFIDENCE_THRESHOLD and valid_until:
            logger.info(f"High OCR confidence ({confidence}). Auto-updating fitness expiry for Asset {asset.asset_code} to {valid_until}")
            asset.fitness_expiry_date = valid_until
            doc.verification_status = "VERIFIED"

        # 4. Step 5: Expiry Warning Check
        if valid_until and valid_until <= (date.today() + timedelta(days=30)):
            alert = Alert(
                id=generate_uuid(),
                mine_id=asset.mine_id,
                zone_id=asset.zone_id,
                title=f"Statutory Fitness Expiring Soon: {asset.asset_code}",
                message=f"Equipment {asset.name} certificate expires on {valid_until}. Please initiate renewal inspection.",
                alert_type="EXPIRY_WARNING",
                severity="HIGH" if valid_until <= date.today() else "MEDIUM",
                channel="IN_APP",
                target_role="SAFETY_OFFICER"
            )
            db.add(alert)

        await audit_service.log_action(
            db=db,
            action="EQUIPMENT_DOCUMENT_PROCESSED_OCR",
            entity_type="EquipmentDocument",
            entity_id=doc.id,
            changes={"confidence": confidence, "expiry_date": str(valid_until)},
            user_id=user_id,
            mine_id=asset.mine_id
        )

        await db.commit()
        await db.refresh(doc)
        return doc

    @classmethod
    async def get_expiring_assets(cls, db: AsyncSession, mine_id: str, days: int = 30) -> List[EquipmentAsset]:
        target_date = date.today() + timedelta(days=days)
        stmt = select(EquipmentAsset).where(
            and_(
                EquipmentAsset.mine_id == mine_id,
                EquipmentAsset.fitness_expiry_date != None,
                EquipmentAsset.fitness_expiry_date <= target_date,
                EquipmentAsset.status == "ACTIVE"
            )
        ).order_by(EquipmentAsset.fitness_expiry_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())


equipment_service = EquipmentService()

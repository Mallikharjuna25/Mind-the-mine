"""
CCTV & Vision Ingestion Service
Orchestrates the 6-step CCTV Detection -> Candidate Violation promotion algorithm.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.config import settings
from app.core.exceptions import EntityNotFoundError
from app.core.logging_config import logger
from app.models.cctv_models import CameraRegistry, DetectionEvent
from app.models.compliance_models import Violation
from app.models.workflow_models import Alert
from app.schemas.cctv_schemas import DetectionIngestRequest
from app.ai.vision.yolo_detector import safety_detector, DetectedObject
import uuid


class CCTVService:

    @classmethod
    async def get_or_create_camera(
        cls,
        db: AsyncSession,
        mine_id: str,
        zone_id: str,
        camera_code: str,
        name: str
    ) -> CameraRegistry:
        stmt = select(CameraRegistry).where(CameraRegistry.camera_code == camera_code)
        res = await db.execute(stmt)
        cam = res.scalars().first()
        if not cam:
            cam = CameraRegistry(
                mine_id=mine_id,
                zone_id=zone_id,
                camera_code=camera_code,
                name=name,
                status="ACTIVE",
                ppe_check_enabled=True,
                restricted_zone_enabled=True,
                fire_smoke_enabled=True
            )
            db.add(cam)
            await db.commit()
            await db.refresh(cam)
        return cam

    @classmethod
    async def process_detection_ingest(
        cls,
        db: AsyncSession,
        payload: DetectionIngestRequest
    ) -> Dict[str, Any]:
        """
        Executes confidence gating, deduplication, and candidate violation promotion.
        """
        # 1. Fetch Camera
        stmt = select(CameraRegistry).where(CameraRegistry.id == payload.camera_id)
        res = await db.execute(stmt)
        camera = res.scalars().first()
        if not camera:
            raise EntityNotFoundError("CameraRegistry", payload.camera_id)

        # 2. Step 1: Threshold Check
        meets_threshold = payload.confidence_score >= settings.CCTV_CONFIDENCE_THRESHOLD

        # 3. Save raw detection event
        event = DetectionEvent(
            mine_id=camera.mine_id,
            zone_id=camera.zone_id,
            camera_id=camera.id,
            detection_type=payload.detection_type,
            raw_class_name=payload.raw_class_name,
            confidence_score=payload.confidence_score,
            bounding_box_json=payload.bounding_box_json,
            frame_timestamp=datetime.now(timezone.utc),
            metadata_json=payload.metadata
        )
        db.add(event)
        await db.flush()

        if not meets_threshold:
            logger.debug(f"Detection {event.id} ({payload.raw_class_name}) below threshold {payload.confidence_score} < {settings.CCTV_CONFIDENCE_THRESHOLD}. Kept as raw log.")
            await db.commit()
            return {"event_id": event.id, "promoted": False, "reason": "BELOW_CONFIDENCE_THRESHOLD"}

        # 4. Step 2: Deduplication Window (within last 30s for same camera & type)
        window_start = datetime.now(timezone.utc) - timedelta(seconds=settings.CCTV_DEDUPLICATION_WINDOW_SECONDS)
        dup_stmt = select(Violation).where(
            and_(
                Violation.camera_id == camera.id,
                Violation.category == payload.detection_type,
                Violation.created_at >= window_start,
                Violation.status.in_(["CANDIDATE", "CONFIRMED"])
            )
        ).order_by(desc(Violation.created_at)).limit(1)
        
        dup_res = await db.execute(dup_stmt)
        existing_violation = dup_res.scalars().first()

        if existing_violation:
            logger.info(f"Duplicate detection within {settings.CCTV_DEDUPLICATION_WINDOW_SECONDS}s. Merging evidence into Violation {existing_violation.violation_code}.")
            event.promoted_to_violation = True
            event.violation_id = existing_violation.id
            await db.commit()
            return {
                "event_id": event.id,
                "promoted": True,
                "violation_id": existing_violation.id,
                "violation_code": existing_violation.violation_code,
                "is_merged": True
            }

        # 5. Step 3: Rule & Severity Resolution
        rule_map = {
            "PPE_VIOLATION": ("CMR 2017 Reg 130 (Protective Equipment)", "MEDIUM"),
            "RESTRICTED_ZONE_INTRUSION": ("DGMS Safety Circular 02/2022 (Unauthorized Danger Zone Entry)", "HIGH"),
            "FIRE_SMOKE": ("CMR 2017 Reg 138 (Spontaneous Combustion & Fire Precautions)", "CRITICAL"),
            "VEHICLE_HAZARD": ("DGMS Tech Circular 04/2023 (HEMM Traffic Separation)", "HIGH")
        }
        rule_ref, severity = rule_map.get(payload.detection_type, ("CMR 2017 General Safety", "MEDIUM"))

        # Generate evidence snapshot
        det_obj = DetectedObject(
            class_name=payload.raw_class_name,
            confidence=payload.confidence_score,
            bbox=payload.bounding_box_json.get("box", [0.4, 0.3, 0.6, 0.7]) if payload.bounding_box_json else [0.4, 0.3, 0.6, 0.7],
            metadata={"detection_type": payload.detection_type}
        )
        evidence_path = safety_detector.process_and_save_evidence(det_obj, camera.camera_code)

        # 6. Step 4: Create Candidate Violation
        v_code = f"VIO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        violation = Violation(
            mine_id=camera.mine_id,
            zone_id=camera.zone_id,
            camera_id=camera.id,
            detection_event_id=event.id,
            violation_code=v_code,
            category=payload.detection_type,
            rule_reference=rule_ref,
            severity=severity,
            status="CANDIDATE",
            confidence=payload.confidence_score,
            description=f"AI Vision detected {payload.raw_class_name.replace('_', ' ')} at {camera.name}.",
            evidence_snapshot_path=evidence_path,
            metadata_json=payload.metadata
        )
        db.add(violation)
        await db.flush()

        event.promoted_to_violation = True
        event.violation_id = violation.id

        # 7. Step 5: Trigger In-App Safety Alert
        alert = Alert(
            mine_id=camera.mine_id,
            zone_id=camera.zone_id,
            violation_id=violation.id,
            title=f"New Candidate Safety Violation: {payload.raw_class_name}",
            message=f"Camera {camera.camera_code} triggered {severity} violation under {rule_ref}.",
            alert_type="SAFETY_BREACH",
            severity=severity,
            channel="IN_APP",
            target_role="SAFETY_OFFICER",
            status="PENDING"
        )
        db.add(alert)

        await db.commit()
        await db.refresh(violation)

        logger.info(f"Promoted detection {event.id} -> Violation {violation.violation_code} [Severity: {severity}]")

        return {
            "event_id": event.id,
            "promoted": True,
            "violation_id": violation.id,
            "violation_code": violation.violation_code,
            "severity": severity,
            "status": violation.status,
            "evidence_snapshot": evidence_path
        }


cctv_service = CCTVService()

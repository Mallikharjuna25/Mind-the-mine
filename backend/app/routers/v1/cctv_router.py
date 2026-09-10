"""
CCTV Camera Registry & Vision Detection Ingestion Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.cctv_models import CameraRegistry, DetectionEvent
from app.schemas.cctv_schemas import CameraCreate, CameraResponse, DetectionIngestRequest, DetectionEventResponse
from app.schemas.common_schemas import ApiResponse
from app.services.cctv_service import cctv_service

router = APIRouter(prefix="/mine", tags=["CCTV AI Monitoring"])


@router.post("/cameras", response_model=ApiResponse[CameraResponse])
async def register_camera(
    payload: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("cctv.camera.manage"))
):
    cam = CameraRegistry(
        mine_id=payload.mine_id,
        zone_id=payload.zone_id,
        camera_code=payload.camera_code,
        name=payload.name,
        rtsp_stream_url=payload.rtsp_stream_url,
        ip_address=payload.ip_address,
        location_desc=payload.location_desc,
        latitude=payload.latitude,
        longitude=payload.longitude,
        resolution=payload.resolution,
        fps=payload.fps,
        coverage_angle=payload.coverage_angle,
        ppe_check_enabled=payload.ppe_check_enabled,
        restricted_zone_enabled=payload.restricted_zone_enabled,
        fire_smoke_enabled=payload.fire_smoke_enabled
    )
    db.add(cam)
    await db.commit()
    await db.refresh(cam)
    return ApiResponse(message="Camera registered successfully", data=CameraResponse.model_validate(cam))


@router.get("/cameras", response_model=ApiResponse[List[CameraResponse]])
async def list_cameras(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CameraRegistry)
    if mine_id:
        stmt = stmt.where(CameraRegistry.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(CameraRegistry.zone_id == zone_id)
    res = await db.execute(stmt)
    cameras = list(res.scalars().all())
    return ApiResponse(data=[CameraResponse.model_validate(c) for c in cameras])


@router.post("/detections/ingest", response_model=ApiResponse[dict])
async def ingest_vision_detection(
    payload: DetectionIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests detection from safety vision AI pipeline and executes confidence-gated promotion.
    """
    result = await cctv_service.process_detection_ingest(db=db, payload=payload)
    return ApiResponse(message="Detection processed", data=result)


@router.get("/detections", response_model=ApiResponse[List[DetectionEventResponse]])
async def list_detections(
    camera_id: Optional[str] = Query(None),
    detection_type: Optional[str] = Query(None),
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DetectionEvent).order_by(DetectionEvent.created_at.desc()).limit(limit)
    if camera_id:
        stmt = stmt.where(DetectionEvent.camera_id == camera_id)
    if detection_type:
        stmt = stmt.where(DetectionEvent.detection_type == detection_type)
    res = await db.execute(stmt)
    detections = list(res.scalars().all())
    return ApiResponse(data=[DetectionEventResponse.model_validate(d) for d in detections])

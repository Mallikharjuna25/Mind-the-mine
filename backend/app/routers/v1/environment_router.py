"""
Environmental Sensor Readings & Gas Telemetry Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.environment_models import EnvironmentalReading
from app.schemas.environment_schemas import EnvironmentalReadingCreate, EnvironmentalReadingResponse
from app.schemas.common_schemas import ApiResponse
from app.services.environment_service import environment_service

router = APIRouter(prefix="/mine", tags=["Environmental Monitoring"])


@router.post("/environmental-readings", response_model=ApiResponse[EnvironmentalReadingResponse])
async def log_environmental_reading(
    payload: EnvironmentalReadingCreate,
    db: AsyncSession = Depends(get_db)
):
    reading = await environment_service.record_reading(db=db, payload=payload)
    return ApiResponse(message="Environmental reading logged", data=EnvironmentalReadingResponse.model_validate(reading))


@router.get("/environmental-readings", response_model=ApiResponse[List[EnvironmentalReadingResponse]])
async def list_environmental_readings(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    is_breach: Optional[bool] = Query(None),
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(EnvironmentalReading).order_by(EnvironmentalReading.reading_timestamp.desc()).limit(limit)
    if mine_id:
        stmt = stmt.where(EnvironmentalReading.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(EnvironmentalReading.zone_id == zone_id)
    if is_breach is not None:
        stmt = stmt.where(EnvironmentalReading.is_breach == is_breach)

    res = await db.execute(stmt)
    readings = list(res.scalars().all())
    return ApiResponse(data=[EnvironmentalReadingResponse.model_validate(r) for r in readings])

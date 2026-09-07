"""
Production Records Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.production_models import ProductionRecord
from app.schemas.production_schemas import ProductionRecordCreate, ProductionRecordResponse
from app.schemas.common_schemas import ApiResponse
from app.services.production_service import production_service

router = APIRouter(prefix="/mine", tags=["Production Compliance & Output"])


@router.post("/production-records", response_model=ApiResponse[ProductionRecordResponse])
async def log_production_record(
    payload: ProductionRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("production.record.create"))
):
    record = await production_service.log_production(db=db, payload=payload, user_id=current_user.sub)
    return ApiResponse(message="Production record logged with variance evaluation", data=ProductionRecordResponse.model_validate(record))


@router.get("/production-records", response_model=ApiResponse[List[ProductionRecordResponse]])
async def list_production_records(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    limit: int = Query(default=30, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductionRecord).order_by(ProductionRecord.shift_date.desc()).limit(limit)
    if mine_id:
        stmt = stmt.where(ProductionRecord.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(ProductionRecord.zone_id == zone_id)

    res = await db.execute(stmt)
    records = list(res.scalars().all())
    return ApiResponse(data=[ProductionRecordResponse.model_validate(r) for r in records])

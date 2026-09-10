"""
Mine & Spatial Zone Registry Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.mine_models import Mine, MineZone
from app.schemas.mine_schemas import MineCreate, MineResponse, MineZoneCreate, MineZoneResponse
from app.schemas.common_schemas import ApiResponse

router = APIRouter(prefix="/mine", tags=["Mines & Zones"])


@router.post("/mines", response_model=ApiResponse[MineResponse])
async def create_mine(
    payload: MineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("cctv.camera.manage"))
):
    mine = Mine(
        mine_code=payload.mine_code,
        name=payload.name,
        subsidiary=payload.subsidiary,
        state=payload.state,
        district=payload.district,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_sqkm=payload.area_sqkm,
        lease_boundary_geojson=payload.lease_boundary_geojson,
        is_active=True
    )
    db.add(mine)
    await db.commit()
    await db.refresh(mine)
    return ApiResponse(message="Mine registered successfully", data=MineResponse.model_validate(mine))


@router.get("/mines", response_model=ApiResponse[List[MineResponse]])
async def list_mines(db: AsyncSession = Depends(get_db)):
    stmt = select(Mine).options(selectinload(Mine.zones)).where(Mine.is_active == True)
    res = await db.execute(stmt)
    mines = list(res.scalars().all())
    return ApiResponse(data=[MineResponse.model_validate(m) for m in mines])


@router.post("/mines/{mine_id}/zones", response_model=ApiResponse[MineZoneResponse])
async def create_zone(
    mine_id: str,
    payload: MineZoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("cctv.camera.manage"))
):
    zone = MineZone(
        mine_id=mine_id,
        zone_code=payload.zone_code,
        name=payload.name,
        zone_type=payload.zone_type,
        polygon_geojson=payload.polygon_geojson,
        risk_weight=payload.risk_weight,
        is_restricted=payload.is_restricted
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return ApiResponse(message="Mine zone created successfully", data=MineZoneResponse.model_validate(zone))


@router.get("/mines/{mine_id}/zones", response_model=ApiResponse[List[MineZoneResponse]])
async def list_mine_zones(mine_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(MineZone).where(MineZone.mine_id == mine_id)
    res = await db.execute(stmt)
    zones = list(res.scalars().all())
    return ApiResponse(data=[MineZoneResponse.model_validate(z) for z in zones])

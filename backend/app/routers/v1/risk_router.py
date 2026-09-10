"""
Unified Risk Engine & Anomaly Detection Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.risk_models import RiskScore, Anomaly
from app.schemas.risk_schemas import RiskScoreComputeRequest, RiskScoreResponse, AnomalyResponse, AnomalyResolveRequest
from app.schemas.common_schemas import ApiResponse
from app.services.risk_engine_service import risk_engine_service
from app.services.anomaly_service import anomaly_service

router = APIRouter(prefix="/mine", tags=["Risk Engine & Anomaly Detection"])


@router.post("/risk-scores/compute", response_model=ApiResponse[List[RiskScoreResponse]])
async def trigger_risk_compute(
    payload: RiskScoreComputeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("risk.score.compute"))
):
    if payload.zone_id:
        score = await risk_engine_service.compute_zone_risk(db=db, mine_id=payload.mine_id, zone_id=payload.zone_id)
        results = [score]
    else:
        results = await risk_engine_service.compute_mine_all_zones(db=db, mine_id=payload.mine_id)

    return ApiResponse(
        message=f"Risk scores recomputed for {len(results)} zone(s)",
        data=[RiskScoreResponse.model_validate(r) for r in results]
    )


@router.get("/risk-scores/latest", response_model=ApiResponse[List[RiskScoreResponse]])
async def get_latest_risk_scores(mine_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(RiskScore).where(RiskScore.mine_id == mine_id).order_by(RiskScore.calculated_at.desc())
    res = await db.execute(stmt)
    all_scores = list(res.scalars().all())

    # Get latest unique per zone
    seen_zones = set()
    latest_per_zone = []
    for s in all_scores:
        if s.zone_id not in seen_zones:
            seen_zones.add(s.zone_id)
            latest_per_zone.append(s)

    return ApiResponse(data=[RiskScoreResponse.model_validate(s) for s in latest_per_zone])


@router.get("/anomalies", response_model=ApiResponse[List[AnomalyResponse]])
async def list_anomalies(
    mine_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Anomaly).order_by(Anomaly.created_at.desc())
    if mine_id:
        stmt = stmt.where(Anomaly.mine_id == mine_id)
    if zone_id:
        stmt = stmt.where(Anomaly.zone_id == zone_id)
    if is_resolved is not None:
        stmt = stmt.where(Anomaly.is_resolved == is_resolved)

    res = await db.execute(stmt)
    anomalies = list(res.scalars().all())
    return ApiResponse(data=[AnomalyResponse.model_validate(a) for a in anomalies])


@router.post("/anomalies/{anomaly_id}/resolve", response_model=ApiResponse[AnomalyResponse])
async def resolve_anomaly(
    anomaly_id: str,
    payload: AnomalyResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("risk.anomaly.manage"))
):
    anomaly = await anomaly_service.resolve_anomaly(
        db=db,
        anomaly_id=anomaly_id,
        note=payload.resolution_note,
        user_id=current_user.sub
    )
    return ApiResponse(message="Anomaly resolved", data=AnomalyResponse.model_validate(anomaly))

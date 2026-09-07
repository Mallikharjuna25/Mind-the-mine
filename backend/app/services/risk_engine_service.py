"""
Risk Engine Service
Computes composite risk scores per mine zone and mine aggregate based on multi-factor signals.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.mine_models import MineZone, Mine
from app.models.compliance_models import Violation
from app.models.environment_models import EnvironmentalReading
from app.models.production_models import ProductionRecord
from app.models.equipment_models import EquipmentAsset
from app.models.risk_models import RiskScore
from app.ai.risk.risk_calculator import risk_calculator
from app.core.logging_config import logger


class RiskEngineService:

    @classmethod
    async def compute_zone_risk(cls, db: AsyncSession, mine_id: str, zone_id: str) -> RiskScore:
        # 1. Fetch zone details
        zone_stmt = select(MineZone).where(and_(MineZone.id == zone_id, MineZone.mine_id == mine_id))
        zone_res = await db.execute(zone_stmt)
        zone = zone_res.scalars().first()
        zone_weight = zone.risk_weight if zone else 1.0

        # 2. Count Active Violations in last 30 days
        since_date = datetime.now(timezone.utc) - timedelta(days=30)
        v_stmt = select(Violation).where(
            and_(
                Violation.mine_id == mine_id,
                Violation.zone_id == zone_id,
                Violation.status.in_(["CANDIDATE", "CONFIRMED"]),
                Violation.created_at >= since_date
            )
        )
        v_res = await db.execute(v_stmt)
        violations = list(v_res.scalars().all())
        active_v_count = len(violations)
        critical_v_count = sum(1 for v in violations if v.severity == "CRITICAL")
        high_v_count = sum(1 for v in violations if v.severity == "HIGH")

        # 3. Count Environmental Breaches in last 7 days
        env_since = datetime.now(timezone.utc) - timedelta(days=7)
        env_stmt = select(func.count(EnvironmentalReading.id)).where(
            and_(
                EnvironmentalReading.mine_id == mine_id,
                EnvironmentalReading.zone_id == zone_id,
                EnvironmentalReading.is_breach == True,
                EnvironmentalReading.reading_timestamp >= env_since
            )
        )
        env_res = await db.execute(env_stmt)
        env_breaches = env_res.scalar() or 0

        # 4. Get Latest Production Variance
        prod_stmt = select(ProductionRecord).where(
            and_(
                ProductionRecord.mine_id == mine_id,
                ProductionRecord.zone_id == zone_id
            )
        ).order_by(ProductionRecord.created_at.desc()).limit(1)
        prod_res = await db.execute(prod_stmt)
        latest_prod = prod_res.scalars().first()
        prod_variance = latest_prod.variance_pct if latest_prod else 0.0

        # 5. Count Overdue / Expiring Equipment
        today = date.today()
        eq_stmt = select(func.count(EquipmentAsset.id)).where(
            and_(
                EquipmentAsset.mine_id == mine_id,
                EquipmentAsset.zone_id == zone_id,
                EquipmentAsset.fitness_expiry_date != None,
                EquipmentAsset.fitness_expiry_date <= today,
                EquipmentAsset.status == "ACTIVE"
            )
        )
        eq_res = await db.execute(eq_stmt)
        overdue_eq = eq_res.scalar() or 0

        # 6. Execute Deterministic Composite Score Calculation
        composite, band, subscores, factors = risk_calculator.calculate_composite_score(
            active_violations_count=active_v_count,
            critical_violations_count=critical_v_count,
            high_violations_count=high_v_count,
            environmental_breaches_count=env_breaches,
            production_variance_pct=prod_variance,
            overdue_equipment_count=overdue_eq,
            zone_risk_weight=zone_weight
        )

        risk_record = RiskScore(
            mine_id=mine_id,
            zone_id=zone_id,
            calculated_at=datetime.now(timezone.utc),
            composite_score=composite,
            risk_band=band,
            violation_subscore=subscores["violation_subscore"],
            environment_subscore=subscores["environment_subscore"],
            production_subscore=subscores["production_subscore"],
            equipment_subscore=subscores["equipment_subscore"],
            contributing_factors_json=factors
        )
        db.add(risk_record)
        await db.commit()
        await db.refresh(risk_record)

        logger.info(f"Recomputed risk score for Zone {zone_id}: Score={composite} ({band})")
        return risk_record

    @classmethod
    async def compute_mine_all_zones(cls, db: AsyncSession, mine_id: str) -> List[RiskScore]:
        zones_stmt = select(MineZone).where(MineZone.mine_id == mine_id)
        zones_res = await db.execute(zones_stmt)
        zones = list(zones_res.scalars().all())

        results = []
        for z in zones:
            score = await cls.compute_zone_risk(db, mine_id, z.id)
            results.append(score)
        return results


risk_engine_service = RiskEngineService()

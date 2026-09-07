"""
Anomaly Scan & Management Service
Scans historical non-compliance events to detect recurring violation patterns.
"""

from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.compliance_models import Violation
from app.models.risk_models import Anomaly
from app.models.mine_models import MineZone
from app.ai.risk.anomaly_detector import anomaly_detector
from app.core.exceptions import EntityNotFoundError
from app.core.logging_config import logger


class AnomalyService:

    @classmethod
    async def scan_zone_recurring_violations(cls, db: AsyncSession, mine_id: str, zone_id: str) -> List[Anomaly]:
        window_start = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(Violation).where(
            and_(
                Violation.mine_id == mine_id,
                Violation.zone_id == zone_id,
                Violation.created_at >= window_start
            )
        )
        res = await db.execute(stmt)
        violations = list(res.scalars().all())

        raw_dicts = [{"id": v.id, "category": v.category, "severity": v.severity} for v in violations]
        detected = anomaly_detector.detect_recurring_violations(raw_dicts, threshold_count=3, window_days=30)

        created_anomalies = []
        for d in detected:
            anomaly = Anomaly(
                mine_id=mine_id,
                zone_id=zone_id,
                anomaly_type=d["anomaly_type"],
                title=d["title"],
                description=d["description"],
                severity=d["severity"],
                metric_name=d["metric_name"],
                expected_value=d["expected_value"],
                observed_value=d["observed_value"],
                deviation_pct=d["deviation_pct"],
                metadata_json=d["metadata"]
            )
            db.add(anomaly)
            created_anomalies.append(anomaly)

        if created_anomalies:
            await db.commit()
            logger.info(f"Flagged {len(created_anomalies)} recurring violation anomalies for zone {zone_id}")

        return created_anomalies

    @classmethod
    async def resolve_anomaly(cls, db: AsyncSession, anomaly_id: str, note: str, user_id: str) -> Anomaly:
        stmt = select(Anomaly).where(Anomaly.id == anomaly_id)
        res = await db.execute(stmt)
        anomaly = res.scalars().first()
        if not anomaly:
            raise EntityNotFoundError("Anomaly", anomaly_id)

        anomaly.is_resolved = True
        anomaly.resolved_by_user_id = user_id
        anomaly.resolved_at = datetime.now(timezone.utc)
        anomaly.resolution_note = note

        await db.commit()
        await db.refresh(anomaly)
        return anomaly


anomaly_service = AnomalyService()

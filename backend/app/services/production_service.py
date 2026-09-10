"""
Production Service
Manages coal output logging, downtime tracking, and variance anomaly detection.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.production_models import ProductionRecord
from app.models.risk_models import Anomaly
from app.schemas.production_schemas import ProductionRecordCreate
from app.ai.risk.anomaly_detector import anomaly_detector
from app.core.logging_config import logger


class ProductionService:

    @classmethod
    async def log_production(
        cls,
        db: AsyncSession,
        payload: ProductionRecordCreate,
        user_id: Optional[str] = None
    ) -> ProductionRecord:
        variance_pct = 0.0
        if payload.target_tonnes > 0:
            variance_pct = round(((payload.actual_tonnes - payload.target_tonnes) / payload.target_tonnes) * 100.0, 2)

        record = ProductionRecord(
            mine_id=payload.mine_id,
            zone_id=payload.zone_id,
            shift_date=payload.shift_date,
            shift_number=payload.shift_number,
            seam_name=payload.seam_name,
            target_tonnes=payload.target_tonnes,
            actual_tonnes=payload.actual_tonnes,
            overburden_cbm=payload.overburden_cbm,
            machinery_trips=payload.machinery_trips,
            downtime_minutes=payload.downtime_minutes,
            downtime_reason=payload.downtime_reason,
            variance_pct=variance_pct,
            logged_by_user_id=user_id
        )
        db.add(record)
        await db.flush()

        # Check for production shortfall anomaly
        anomaly_data = anomaly_detector.detect_production_anomalies(
            target_tonnes=payload.target_tonnes,
            actual_tonnes=payload.actual_tonnes,
            downtime_minutes=payload.downtime_minutes
        )
        if anomaly_data:
            anomaly = Anomaly(
                mine_id=payload.mine_id,
                zone_id=payload.zone_id,
                anomaly_type=anomaly_data["anomaly_type"],
                title=anomaly_data["title"],
                description=anomaly_data["description"],
                severity=anomaly_data["severity"],
                metric_name=anomaly_data["metric_name"],
                expected_value=anomaly_data["expected_value"],
                observed_value=anomaly_data["observed_value"],
                deviation_pct=anomaly_data["deviation_pct"],
                metadata_json=anomaly_data["metadata"]
            )
            db.add(anomaly)
            logger.warning(f"Production anomaly flagged for zone {payload.zone_id}: {anomaly_data['title']}")

        await db.commit()
        await db.refresh(record)
        return record


production_service = ProductionService()

"""
Environmental Monitoring & Gas Telemetry Service
Ingests atmospheric and environmental telemetry, evaluating DGMS safety thresholds.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.environment_models import EnvironmentalReading
from app.models.workflow_models import Alert
from app.schemas.environment_schemas import EnvironmentalReadingCreate
from app.core.logging_config import logger


class EnvironmentService:

    @classmethod
    async def record_reading(cls, db: AsyncSession, payload: EnvironmentalReadingCreate) -> EnvironmentalReading:
        breaches: List[Dict[str, Any]] = []
        is_breach = False

        # DGMS Coal Mine Statutory Safety Threshold Checks
        # 1. Methane (CH4)
        if payload.methane_ch4_pct is not None and payload.methane_ch4_pct > 0.75:
            is_breach = True
            breaches.append({
                "gas": "Methane (CH4)",
                "value": payload.methane_ch4_pct,
                "threshold": 0.75,
                "unit": "%",
                "severity": "CRITICAL" if payload.methane_ch4_pct >= 1.25 else "HIGH",
                "rule": "CMR 2017 Reg 169 (Inflammable Gas Standards)"
            })

        # 2. Carbon Monoxide (CO)
        if payload.carbon_monoxide_co_ppm is not None and payload.carbon_monoxide_co_ppm > 50.0:
            is_breach = True
            breaches.append({
                "gas": "Carbon Monoxide (CO)",
                "value": payload.carbon_monoxide_co_ppm,
                "threshold": 50.0,
                "unit": "ppm",
                "severity": "CRITICAL",
                "rule": "CMR 2017 Reg 171 (Detection of Spontaneous Heating)"
            })

        # 3. Oxygen (O2)
        if payload.oxygen_o2_pct is not None and payload.oxygen_o2_pct < 19.0:
            is_breach = True
            breaches.append({
                "gas": "Oxygen (O2)",
                "value": payload.oxygen_o2_pct,
                "threshold": 19.0,
                "unit": "%",
                "severity": "CRITICAL",
                "rule": "CMR 2017 Reg 168 (Adequate Mine Ventilation)"
            })

        # 4. Particulate Matter (PM2.5 / PM10)
        if payload.dust_pm25 is not None and payload.dust_pm25 > 120.0:
            is_breach = True
            breaches.append({
                "pollutant": "PM2.5",
                "value": payload.dust_pm25,
                "threshold": 120.0,
                "unit": "ug/m3",
                "severity": "MEDIUM",
                "rule": "MoEFCC Environmental Standards"
            })

        reading = EnvironmentalReading(
            mine_id=payload.mine_id,
            zone_id=payload.zone_id,
            sensor_code=payload.sensor_code,
            reading_timestamp=payload.reading_timestamp or datetime.now(timezone.utc),
            methane_ch4_pct=payload.methane_ch4_pct,
            carbon_monoxide_co_ppm=payload.carbon_monoxide_co_ppm,
            oxygen_o2_pct=payload.oxygen_o2_pct,
            dust_pm25=payload.dust_pm25,
            dust_pm10=payload.dust_pm10,
            temperature_c=payload.temperature_c,
            humidity_pct=payload.humidity_pct,
            noise_db=payload.noise_db,
            is_breach=is_breach,
            breach_details_json={"breaches": breaches} if breaches else None,
            source=payload.source
        )
        db.add(reading)
        await db.flush()

        # If gas threshold breached, trigger high-priority gas alarm alert
        if is_breach:
            highest_sev = "CRITICAL" if any(b.get("severity") == "CRITICAL" for b in breaches) else "HIGH"
            alert = Alert(
                mine_id=payload.mine_id,
                zone_id=payload.zone_id,
                reading_id=reading.id,
                title=f"HAZARDOUS GAS BREACH: {breaches[0]['gas'] if 'gas' in breaches[0] else 'Air Quality'}",
                message=f"Sensor {payload.sensor_code} recorded abnormal reading ({breaches[0]['value']}). Immediate inspection / evacuation protocol required.",
                alert_type="GAS_ALARM",
                severity=highest_sev,
                channel="IN_APP",
                target_role="SAFETY_OFFICER"
            )
            db.add(alert)
            logger.warning(f"Environmental breach alert triggered for sensor {payload.sensor_code} in zone {payload.zone_id}")

        await db.commit()
        await db.refresh(reading)
        return reading


environment_service = EnvironmentService()

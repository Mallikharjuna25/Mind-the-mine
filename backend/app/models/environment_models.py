"""
Environmental Sensor Readings & Gas Telemetry Models
Ingests toxic gas ($CH_4$, $CO$, $O_2$), particulate matter (PM2.5/PM10), temperature, humidity,
and noise from underground LoRa nodes and surface IoT stations.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin, utc_now


class EnvironmentalReading(BaseModelMixin):
    __tablename__ = "environmental_readings"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sensor_code = Column(String(50), nullable=False, index=True)
    reading_timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    
    # Gas Telemetry
    methane_ch4_pct = Column(Float, nullable=True)  # DGMS Threshold: > 0.75% Warning, > 1.25% Evacuate
    carbon_monoxide_co_ppm = Column(Float, nullable=True)  # Threshold: > 50 ppm Danger
    oxygen_o2_pct = Column(Float, nullable=True)  # Threshold: < 19.0% Danger
    
    # Particulate & Climate
    dust_pm25 = Column(Float, nullable=True)  # ug/m3
    dust_pm10 = Column(Float, nullable=True)  # ug/m3
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    noise_db = Column(Float, nullable=True)
    air_quality_index = Column(Float, nullable=True)
    
    # Breach Evaluation
    is_breach = Column(Boolean, default=False, nullable=False, index=True)
    breach_details_json = Column(JSON, nullable=True)
    source = Column(String(50), default="IOT_SENSOR", nullable=False)  # IOT_SENSOR, LORA_TELEMETRY, MANUAL_SAMPLE

    mine = relationship("Mine", back_populates="environmental_readings")
    zone = relationship("MineZone", back_populates="environmental_readings")

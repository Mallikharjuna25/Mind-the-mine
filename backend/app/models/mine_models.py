"""
Mine & Mine Zone Database Models
Supports spatial leasehold boundaries and zone geofencing stored as GeoJSON for SQLite,
with clean migration path to PostGIS Geometry columns.
"""

from sqlalchemy import Column, String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin


class Mine(BaseModelMixin):
    __tablename__ = "mines"

    mine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    subsidiary = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_sqkm = Column(Float, default=12.5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    lease_boundary_geojson = Column(JSON, nullable=True)

    # Relationships with eager selectin loading for async sessions
    zones = relationship("MineZone", back_populates="mine", cascade="all, delete-orphan", lazy="selectin")
    users = relationship("User", back_populates="mine", lazy="selectin")
    cameras = relationship("CameraRegistry", back_populates="mine")
    violations = relationship("Violation", back_populates="mine")
    equipment = relationship("EquipmentAsset", back_populates="mine")
    environmental_readings = relationship("EnvironmentalReading", back_populates="mine")
    production_records = relationship("ProductionRecord", back_populates="mine")
    risk_scores = relationship("RiskScore", back_populates="mine")


class MineZone(BaseModelMixin):
    __tablename__ = "mine_zones"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    zone_type = Column(String(50), nullable=False)
    
    polygon_geojson = Column(JSON, nullable=True)
    risk_weight = Column(Float, default=1.0, nullable=False)
    is_restricted = Column(Boolean, default=False, nullable=False)

    mine = relationship("Mine", back_populates="zones")
    cameras = relationship("CameraRegistry", back_populates="zone")
    violations = relationship("Violation", back_populates="zone")
    equipment = relationship("EquipmentAsset", back_populates="zone")
    environmental_readings = relationship("EnvironmentalReading", back_populates="zone")
    risk_scores = relationship("RiskScore", back_populates="zone")

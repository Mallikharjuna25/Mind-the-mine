"""
Production Output & Shift Performance Models
Tracks extraction volume, overburden removal, downtime, and operational variances.
"""

from datetime import date
from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin


class ProductionRecord(BaseModelMixin):
    __tablename__ = "production_records"

    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = Column(String(36), ForeignKey("mine_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    shift_date = Column(Date, nullable=False, index=True)
    shift_number = Column(Integer, default=1, nullable=False)  # 1 (Morning), 2 (Afternoon), 3 (Night)
    seam_name = Column(String(100), default="Main Seam", nullable=False)
    
    target_tonnes = Column(Float, nullable=False)
    actual_tonnes = Column(Float, nullable=False)
    overburden_cbm = Column(Float, default=0.0, nullable=False)
    machinery_trips = Column(Integer, default=0, nullable=False)
    
    downtime_minutes = Column(Integer, default=0, nullable=False)
    downtime_reason = Column(String(255), nullable=True)
    
    # Calculated Variance: ((actual - target) / target) * 100
    variance_pct = Column(Float, default=0.0, nullable=False)
    logged_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    mine = relationship("Mine", back_populates="production_records")

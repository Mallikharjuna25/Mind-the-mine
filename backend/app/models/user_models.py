"""
User & Authentication Database Models
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModelMixin


class User(BaseModelMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)  # MINE_MANAGER, SAFETY_OFFICER, etc.
    designation = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Associated Mine (Multi-tenant partition)
    mine_id = Column(String(36), ForeignKey("mines.id", ondelete="SET NULL"), nullable=True, index=True)
    
    mine = relationship("Mine", back_populates="users")

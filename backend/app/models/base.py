"""
Base SQLAlchemy Model
Provides standard UUID primary key, audit timestamps, and soft deletion flag.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseModelMixin(Base):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    def __init__(self, **kwargs):
        if "id" not in kwargs or kwargs["id"] is None:
            kwargs["id"] = generate_uuid()
        if "created_at" not in kwargs or kwargs["created_at"] is None:
            kwargs["created_at"] = utc_now()
        if "updated_at" not in kwargs or kwargs["updated_at"] is None:
            kwargs["updated_at"] = utc_now()
        super().__init__(**kwargs)

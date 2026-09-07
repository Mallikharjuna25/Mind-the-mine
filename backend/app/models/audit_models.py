"""
Immutable Audit Trail Model
Maintains cryptographic SHA-256 hash chaining of all statutory actions and verifications.
"""

import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime
from app.models.base import BaseModelMixin, utc_now


class AuditLog(BaseModelMixin):
    __tablename__ = "audit_logs"

    mine_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., VIOLATION_VERIFIED, OCR_CERTIFICATE_UPLOADED, ACTION_CLOSED
    entity_type = Column(String(100), nullable=False, index=True)  # Violation, EquipmentAsset, CorrectiveAction
    entity_id = Column(String(36), nullable=False, index=True)
    
    user_id = Column(String(36), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    changes_json = Column(JSON, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    block_hash = Column(String(64), nullable=False)

    @classmethod
    def calculate_hash(cls, prev_hash: str, action: str, entity_type: str, entity_id: str, changes: dict, timestamp: datetime) -> str:
        payload = f"{prev_hash}|{action}|{entity_type}|{entity_id}|{json.dumps(changes, sort_keys=True)}|{timestamp.isoformat()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

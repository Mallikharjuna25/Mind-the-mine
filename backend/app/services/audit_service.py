import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.module2_models import AuditTrailEntry

class AuditService:
    @staticmethod
    def log_event(db: Session, entity_type: str, entity_id: str, action: str, performed_by: str, details: dict):
        payload_str = f"{entity_type}:{entity_id}:{action}:{performed_by}:{json.dumps(details, sort_keys=True)}"
        sha256 = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        entry = AuditTrailEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            performed_by=performed_by,
            details=details,
            timestamp=datetime.now(timezone.utc),
            sha256_hash=sha256
        )
        db.add(entry)
        db.commit()
        return entry

"""
Audit Service
Manages SHA-256 chained tamper-evident audit logs for statutory governance.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.audit_models import AuditLog
from app.core.logging_config import logger


class AuditService:
    @classmethod
    async def log_action(
        cls,
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Dict[str, Any],
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        mine_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Creates an audit record with cryptographic hash chaining.
        """
        # Fetch latest audit log to get previous hash
        stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(1)
        res = await db.execute(stmt)
        latest = res.scalars().first()

        prev_hash = latest.block_hash if latest else "GENESIS_MINEGUARD_BLOCK"
        now = datetime.now(timezone.utc)
        block_hash = AuditLog.calculate_hash(prev_hash, action, entity_type, entity_id, changes, now)

        audit_entry = AuditLog(
            mine_id=mine_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            changes_json=changes,
            previous_hash=prev_hash,
            block_hash=block_hash,
            created_at=now
        )
        db.add(audit_entry)
        await db.flush()
        logger.info(f"Audit log recorded: {action} on {entity_type}:{entity_id} [Hash: {block_hash[:10]}...]")
        return audit_entry

    @staticmethod
    def log_event(db, entity_type: str, entity_id: str, action: str, performed_by: str, details: dict):
        """
        Synchronous audit trail logging for Module 2 Field Inspection events.
        """
        import hashlib
        import json
        from app.models.module2_models import AuditTrailEntry

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


audit_service = AuditService()

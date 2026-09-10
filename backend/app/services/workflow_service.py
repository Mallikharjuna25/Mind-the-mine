"""
Workflow, Corrective Actions & SLA Escalation Service
Manages Remediation Lifecycles and 3-Tier SLA Escalation Timers.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.config import settings
from app.core.exceptions import EntityNotFoundError, InvalidStateTransitionError
from app.core.logging_config import logger
from app.models.workflow_models import Alert, CorrectiveAction, Escalation
from app.models.compliance_models import Violation
from app.schemas.workflow_schemas import CorrectiveActionCreate, CorrectiveActionVerifyRequest
from app.services.audit_service import audit_service


class WorkflowService:

    @classmethod
    async def acknowledge_alert(cls, db: AsyncSession, alert_id: str, user_id: str) -> Alert:
        stmt = select(Alert).where(Alert.id == alert_id)
        res = await db.execute(stmt)
        alert = res.scalars().first()
        if not alert:
            raise EntityNotFoundError("Alert", alert_id)

        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by_user_id = user_id

        await db.commit()
        await db.refresh(alert)
        logger.info(f"Alert {alert.id} acknowledged by user {user_id}. SLA timer stopped.")
        return alert

    @classmethod
    async def create_corrective_action(
        cls,
        db: AsyncSession,
        payload: CorrectiveActionCreate,
        user_id: Optional[str] = None
    ) -> CorrectiveAction:
        action_code = f"CAPA-{datetime.now(timezone.utc).strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"

        action = CorrectiveAction(
            mine_id=payload.mine_id,
            violation_id=payload.violation_id,
            anomaly_id=payload.anomaly_id,
            action_code=action_code,
            title=payload.title,
            description=payload.description,
            assigned_to_user_id=payload.assigned_to_user_id,
            assigned_to_contractor=payload.assigned_to_contractor,
            priority=payload.priority,
            deadline=payload.deadline,
            status="OPEN"
        )
        db.add(action)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="CORRECTIVE_ACTION_CREATED",
            entity_type="CorrectiveAction",
            entity_id=action.id,
            changes={"action_code": action.action_code, "priority": action.priority},
            user_id=user_id,
            mine_id=payload.mine_id
        )

        await db.commit()
        await db.refresh(action)
        return action

    @classmethod
    async def verify_and_close_action(
        cls,
        db: AsyncSession,
        action_id: str,
        payload: CorrectiveActionVerifyRequest,
        user_id: str
    ) -> CorrectiveAction:
        stmt = select(CorrectiveAction).where(CorrectiveAction.id == action_id)
        res = await db.execute(stmt)
        action = res.scalars().first()
        if not action:
            raise EntityNotFoundError("CorrectiveAction", action_id)

        valid_transitions = {
            "OPEN": ["IN_PROGRESS", "RESOLVED"],
            "IN_PROGRESS": ["PENDING_VERIFICATION", "RESOLVED"],
            "PENDING_VERIFICATION": ["CLOSED", "REJECTED", "RESOLVED"],
            "RESOLVED": ["CLOSED"]
        }

        action.status = payload.status
        action.remediation_notes = payload.remediation_notes
        if payload.proof_files_json:
            action.proof_files_json = payload.proof_files_json

        if payload.status == "CLOSED":
            action.closed_at = datetime.now(timezone.utc)
            action.closed_by_user_id = user_id

            # Also mark linked violation as RESOLVED
            if action.violation_id:
                v_stmt = select(Violation).where(Violation.id == action.violation_id)
                v_res = await db.execute(v_stmt)
                v = v_res.scalars().first()
                if v:
                    v.status = "RESOLVED"

        await audit_service.log_action(
            db=db,
            action=f"CORRECTIVE_ACTION_{payload.status}",
            entity_type="CorrectiveAction",
            entity_id=action.id,
            changes={"new_status": payload.status, "notes": payload.remediation_notes},
            user_id=user_id,
            mine_id=action.mine_id
        )

        await db.commit()
        await db.refresh(action)
        return action

    @classmethod
    async def evaluate_sla_escalations(cls, db: AsyncSession) -> List[Escalation]:
        """
        Scans all unacknowledged alerts / overdue corrective actions and triggers SLA escalations.
        Level 1 (15m): Safety Officer -> Mine Manager
        Level 2 (60m): Mine Manager -> Director Technical / Corporate
        """
        now = datetime.now(timezone.utc)
        escalations_created = []

        # Find unacknowledged CRITICAL or HIGH alerts
        stmt = select(Alert).where(
            and_(
                Alert.status == "PENDING",
                Alert.severity.in_(["HIGH", "CRITICAL"])
            )
        )
        res = await db.execute(stmt)
        pending_alerts = list(res.scalars().all())

        for alert in pending_alerts:
            elapsed_minutes = (now - alert.sent_at.replace(tzinfo=timezone.utc if alert.sent_at.tzinfo is None else alert.sent_at.tzinfo)).total_seconds() / 60.0
            
            # Check existing escalation level
            esc_stmt = select(Escalation).where(Escalation.alert_id == alert.id).order_by(Escalation.level.desc())
            esc_res = await db.execute(esc_stmt)
            highest_esc = esc_res.scalars().first()
            current_level = highest_esc.level if highest_esc else 0

            # Level 1 Escalation (after 15 minutes)
            if elapsed_minutes >= settings.SLA_LEVEL_1_MINUTES and current_level < 1:
                esc = Escalation(
                    alert_id=alert.id,
                    level=1,
                    escalated_from_role="SAFETY_OFFICER",
                    escalated_to_role="MINE_MANAGER",
                    reason=f"SLA Breach: {alert.severity} alert unacknowledged for >{settings.SLA_LEVEL_1_MINUTES} minutes."
                )
                db.add(esc)
                alert.status = "ESCALATED"
                escalations_created.append(esc)

            # Level 2 Escalation (after 60 minutes)
            elif elapsed_minutes >= settings.SLA_LEVEL_2_MINUTES and current_level < 2:
                esc = Escalation(
                    alert_id=alert.id,
                    level=2,
                    escalated_from_role="MINE_MANAGER",
                    escalated_to_role="CIL_CORPORATE",
                    reason=f"SLA Level 2 Breach: Unacknowledged for >{settings.SLA_LEVEL_2_MINUTES} minutes. Escalated to Corporate HQ."
                )
                db.add(esc)
                escalations_created.append(esc)

        if escalations_created:
            await db.commit()
            logger.info(f"Triggered {len(escalations_created)} automated SLA escalations.")

        return escalations_created


workflow_service = WorkflowService()

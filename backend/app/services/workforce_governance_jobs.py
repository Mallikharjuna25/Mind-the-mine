"""
Workforce Governance Automated Expiry & Compliance Monitoring Service (Module 3)
Evaluates statutory rules, monitors temporal expiry thresholds, and creates deduplicated
governance alerts and audit logs.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.base import generate_uuid, utc_now
from app.models.contractor_models import Contractor, Contract
from app.models.worker_models import Worker, WorkerPass, WorkerInduction
from app.models.governance_models import Grievance, ApprovalRequest
from app.models.workflow_models import Alert
from app.services.audit_service import audit_service
from app.core.logging_config import logger


class WorkforceGovernanceJobs:

    @classmethod
    async def evaluate_all_expiries_and_slas(
        cls, db: AsyncSession, mine_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive statutory compliance and temporal checks across:
        1. Contractor Contracts & Licenses
        2. Worker RFID Access Passes
        3. DGMS Safety Inductions & Form O/P Medical Fitness
        4. Overdue Grievance SLAs
        5. Pending Governance Approvals
        """
        today = date.today()
        now = utc_now()
        thirty_days = today + timedelta(days=30)
        fifteen_days = today + timedelta(days=15)

        alerts_created = 0
        summary = {
            "expiring_contracts": 0,
            "expired_contracts": 0,
            "expiring_passes": 0,
            "expired_passes": 0,
            "expiring_inductions": 0,
            "expired_inductions": 0,
            "overdue_grievances": 0,
            "pending_approvals": 0,
            "alerts_dispatched": 0,
        }

        # 1. Check Contracts Expiry
        c_stmt = select(Contract).where(and_(Contract.status.in_(["ACTIVE", "EXPIRING_SOON"]), Contract.is_deleted == False))
        if mine_id:
            c_stmt = c_stmt.where(Contract.mine_id == mine_id)
        contracts = (await db.execute(c_stmt)).scalars().all()

        for c in contracts:
            if c.end_date < today:
                summary["expired_contracts"] += 1
                c.status = "EXPIRED"
                # Check if alert already exists
                if not await cls._alert_exists(db, c.mine_id, f"EXPIRED_CONTRACT_{c.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=c.mine_id,
                        title=f"Contract Expired: {c.contract_number}",
                        message=f"Contract '{c.title}' ended on {c.end_date}. Commercial and site operations must be halted or renewed immediately.",
                        alert_type="EXPIRY_WARNING",
                        severity="HIGH",
                        dedup_key=f"EXPIRED_CONTRACT_{c.id}"
                    )
                    alerts_created += 1
            elif c.end_date <= thirty_days:
                summary["expiring_contracts"] += 1
                c.status = "EXPIRING_SOON"
                if not await cls._alert_exists(db, c.mine_id, f"EXPIRING_CONTRACT_{c.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=c.mine_id,
                        title=f"Contract Expiring Soon: {c.contract_number}",
                        message=f"Contract '{c.title}' expires in {(c.end_date - today).days} days ({c.end_date}). Initiate renewal review.",
                        alert_type="EXPIRY_WARNING",
                        severity="MEDIUM",
                        dedup_key=f"EXPIRING_CONTRACT_{c.id}"
                    )
                    alerts_created += 1

        # 2. Check Worker Passes Expiry
        p_stmt = select(WorkerPass).where(and_(WorkerPass.status == "ACTIVE", WorkerPass.is_deleted == False))
        if mine_id:
            p_stmt = p_stmt.where(WorkerPass.mine_id == mine_id)
        passes = (await db.execute(p_stmt)).scalars().all()

        for p in passes:
            if p.expiry_date < today:
                summary["expired_passes"] += 1
                p.status = "EXPIRED"
                if not await cls._alert_exists(db, p.mine_id, f"EXPIRED_PASS_{p.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=p.mine_id,
                        title=f"Worker RFID Pass Expired: {p.pass_number}",
                        message=f"RFID pass UID '{p.rfid_uid}' expired on {p.expiry_date}. Automated gate access has been restricted.",
                        alert_type="EXPIRY_WARNING",
                        severity="HIGH",
                        dedup_key=f"EXPIRED_PASS_{p.id}"
                    )
                    alerts_created += 1
            elif p.expiry_date <= fifteen_days:
                summary["expiring_passes"] += 1
                if not await cls._alert_exists(db, p.mine_id, f"EXPIRING_PASS_{p.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=p.mine_id,
                        title=f"Worker RFID Pass Expiring Soon: {p.pass_number}",
                        message=f"RFID pass UID '{p.rfid_uid}' expires on {p.expiry_date}. Schedule pass renewal.",
                        alert_type="EXPIRY_WARNING",
                        severity="LOW",
                        dedup_key=f"EXPIRING_PASS_{p.id}"
                    )
                    alerts_created += 1

        # 3. Check DGMS Inductions Expiry
        i_stmt = select(WorkerInduction).where(and_(WorkerInduction.status == "COMPLETED", WorkerInduction.is_deleted == False))
        if mine_id:
            i_stmt = i_stmt.where(WorkerInduction.mine_id == mine_id)
        inductions = (await db.execute(i_stmt)).scalars().all()

        for ind in inductions:
            if ind.expiry_date < today:
                summary["expired_inductions"] += 1
                ind.status = "EXPIRED"
                if not await cls._alert_exists(db, ind.mine_id, f"EXPIRED_INDUCTION_{ind.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=ind.mine_id,
                        title=f"DGMS Induction Expired: {ind.training_title}",
                        message=f"Worker statutory induction expired on {ind.expiry_date}. Worker safety clearance is now SUSPENDED.",
                        alert_type="SAFETY_BREACH",
                        severity="HIGH",
                        dedup_key=f"EXPIRED_INDUCTION_{ind.id}"
                    )
                    alerts_created += 1
            elif ind.expiry_date <= thirty_days:
                summary["expiring_inductions"] += 1
                if not await cls._alert_exists(db, ind.mine_id, f"EXPIRING_INDUCTION_{ind.id}"):
                    await cls._create_alert(
                        db=db,
                        mine_id=ind.mine_id,
                        title=f"DGMS Induction Renewal Due: {ind.training_title}",
                        message=f"Induction expires in {(ind.expiry_date - today).days} days. Enroll worker in upcoming VTC refresher batch.",
                        alert_type="EXPIRY_WARNING",
                        severity="MEDIUM",
                        dedup_key=f"EXPIRING_INDUCTION_{ind.id}"
                    )
                    alerts_created += 1

        # 4. Check Overdue Grievance SLAs
        g_stmt = select(Grievance).where(
            and_(
                Grievance.status.in_(["OPEN", "ASSIGNED", "UNDER_REVIEW", "IN_PROGRESS"]),
                Grievance.is_deleted == False
            )
        )
        if mine_id:
            g_stmt = g_stmt.where(Grievance.mine_id == mine_id)
        grievances = (await db.execute(g_stmt)).scalars().all()

        for g in grievances:
            # Handle naive datetime vs timezone-aware comparison safely
            deadline = g.sla_deadline
            if deadline:
                if deadline.tzinfo is None and now.tzinfo is not None:
                    deadline = deadline.replace(tzinfo=timezone.utc)
                elif deadline.tzinfo is not None and now.tzinfo is None:
                    deadline = deadline.replace(tzinfo=None)

                if deadline < now:
                    summary["overdue_grievances"] += 1
                    g.is_escalated = True
                    if not await cls._alert_exists(db, g.mine_id, f"OVERDUE_GRIEVANCE_{g.id}"):
                        await cls._create_alert(
                            db=db,
                            mine_id=g.mine_id,
                            title=f"Grievance SLA Breach: {g.title}",
                            message=f"Grievance '{g.title}' ({g.priority} priority) exceeded statutory SLA deadline at {g.sla_deadline.isoformat()}. Escalated to Mine Manager.",
                            alert_type="SAFETY_BREACH",
                            severity="CRITICAL" if g.priority in ("CRITICAL", "HIGH") else "HIGH",
                            dedup_key=f"OVERDUE_GRIEVANCE_{g.id}"
                        )
                        alerts_created += 1

        # 5. Pending Approvals count
        app_stmt = select(ApprovalRequest).where(and_(ApprovalRequest.status == "PENDING", ApprovalRequest.is_deleted == False))
        if mine_id:
            app_stmt = app_stmt.where(ApprovalRequest.mine_id == mine_id)
        pending_apps = (await db.execute(app_stmt)).scalars().all()
        summary["pending_approvals"] = len(pending_apps)

        summary["alerts_dispatched"] = alerts_created
        await db.commit()
        logger.info(f"Workforce governance job completed: {summary}")
        return summary

    @classmethod
    async def _alert_exists(cls, db: AsyncSession, mine_id: str, dedup_key: str) -> bool:
        stmt = select(Alert).where(
            and_(
                Alert.mine_id == mine_id,
                Alert.message.contains(dedup_key),
                Alert.is_deleted == False
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first() is not None

    @classmethod
    async def _create_alert(
        cls,
        db: AsyncSession,
        mine_id: str,
        title: str,
        message: str,
        alert_type: str,
        severity: str,
        dedup_key: str
    ):
        alert = Alert(
            id=generate_uuid(),
            mine_id=mine_id,
            zone_id="MINE_WIDE",
            title=title,
            message=f"{message} [Ref: {dedup_key}]",
            alert_type=alert_type,
            severity=severity,
            channel="IN_APP",
            target_role="SAFETY_OFFICER",
            status="PENDING"
        )
        db.add(alert)


workforce_jobs = WorkforceGovernanceJobs()

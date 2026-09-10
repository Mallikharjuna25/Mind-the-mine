"""
Worker & Compliance Management Service
Orchestrates Worker Registry, Attendance, Training, Certifications, PPE Eligibility, Work Authorization,
Automated Alerts, and Reporting Summaries.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, DuplicateEntityError, InvalidStateTransitionError
from app.core.logging_config import logger
from app.models.base import generate_uuid, utc_now
from app.models.worker_models import (
    Worker, WorkerAttendance, WorkerTraining, WorkerCertification, WorkerPPE,
    WorkerAuthorization, WorkerInsurance, WorkerLeave
)
from app.models.workflow_models import Alert
from app.schemas.worker_schemas import (
    WorkerCreate, WorkerUpdate, WorkerAttendanceCreate, WorkerTrainingCreate,
    WorkerCertificationCreate, WorkerPPECreate, WorkerAuthorizationCreate,
    WorkerInsuranceCreate, WorkerLeaveCreate, WorkerLeaveAction,
    WorkerDashboardStats, WorkerReportsSummary
)
from app.services.audit_service import audit_service


class WorkerService:

    @classmethod
    async def create_worker(
        cls, db: AsyncSession, payload: WorkerCreate, user_id: Optional[str] = None
    ) -> Worker:
        # Check duplicate employee_id
        stmt = select(Worker).where(
            and_(Worker.employee_id == payload.employee_id, Worker.is_deleted == False)
        )
        res = await db.execute(stmt)
        if res.scalars().first():
            raise DuplicateEntityError("Worker", "employee_id", payload.employee_id)

        worker = Worker(
            id=generate_uuid(),
            mine_id=payload.mine_id,
            contractor_id=payload.contractor_id,
            employee_id=payload.employee_id,
            full_name=payload.full_name,
            department=payload.department,
            role=payload.role,
            email=payload.email,
            phone=payload.phone,
            emergency_contact_name=payload.emergency_contact_name,
            emergency_contact_phone=payload.emergency_contact_phone,
            joining_date=payload.joining_date,
            status=payload.status
        )
        db.add(worker)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="WORKER_CREATED",
            entity_type="Worker",
            entity_id=worker.id,
            changes={"employee_id": worker.employee_id, "full_name": worker.full_name},
            user_id=user_id,
            mine_id=payload.mine_id
        )
        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def get_worker(cls, db: AsyncSession, worker_id: str) -> Worker:
        stmt = select(Worker).where(
            and_(Worker.id == worker_id, Worker.is_deleted == False)
        ).options(
            selectinload(Worker.attendances),
            selectinload(Worker.trainings),
            selectinload(Worker.certifications),
            selectinload(Worker.ppes),
            selectinload(Worker.authorizations)
        )
        res = await db.execute(stmt)
        worker = res.scalars().first()
        if not worker:
            raise EntityNotFoundError("Worker", worker_id)
        return worker

    @classmethod
    async def list_workers(
        cls,
        db: AsyncSession,
        mine_id: Optional[str] = None,
        contractor_id: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Worker]:
        stmt = select(Worker).where(Worker.is_deleted == False).options(
            selectinload(Worker.attendances),
            selectinload(Worker.trainings),
            selectinload(Worker.certifications),
            selectinload(Worker.ppes),
            selectinload(Worker.authorizations)
        )

        if mine_id:
            stmt = stmt.where(Worker.mine_id == mine_id)
        if contractor_id:
            stmt = stmt.where(Worker.contractor_id == contractor_id)
        if department:
            stmt = stmt.where(Worker.department == department)
        if status:
            stmt = stmt.where(Worker.status == status)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Worker.full_name.ilike(pattern),
                    Worker.employee_id.ilike(pattern),
                    Worker.phone.ilike(pattern),
                    Worker.role.ilike(pattern)
                )
            )

        stmt = stmt.order_by(Worker.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def update_worker(
        cls, db: AsyncSession, worker_id: str, payload: WorkerUpdate, user_id: Optional[str] = None
    ) -> Worker:
        worker = await cls.get_worker(db, worker_id)

        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            if val is not None:
                setattr(worker, key, val)

        worker.updated_at = utc_now()
        await audit_service.log_action(
            db=db,
            action="WORKER_UPDATED",
            entity_type="Worker",
            entity_id=worker.id,
            changes=update_data,
            user_id=user_id,
            mine_id=worker.mine_id
        )
        await db.commit()
        await db.refresh(worker)
        return worker

    @classmethod
    async def delete_worker(cls, db: AsyncSession, worker_id: str, user_id: Optional[str] = None) -> bool:
        worker = await cls.get_worker(db, worker_id)
        worker.is_deleted = True
        worker.status = "INACTIVE"
        worker.updated_at = utc_now()

        await audit_service.log_action(
            db=db,
            action="WORKER_DELETED",
            entity_type="Worker",
            entity_id=worker.id,
            changes={"status": "INACTIVE", "is_deleted": True},
            user_id=user_id,
            mine_id=worker.mine_id
        )
        await db.commit()
        return True

    # ------------------ ATTENDANCE MANAGEMENT ------------------

    @classmethod
    async def mark_attendance(
        cls, db: AsyncSession, worker_id: str, payload: WorkerAttendanceCreate, user_id: Optional[str] = None
    ) -> WorkerAttendance:
        worker = await cls.get_worker(db, worker_id)

        check_in_time = payload.check_in or utc_now()

        att = WorkerAttendance(
            id=generate_uuid(),
            worker_id=worker.id,
            mine_id=worker.mine_id,
            shift=payload.shift,
            check_in=check_in_time,
            check_out=payload.check_out,
            status=payload.status
        )
        db.add(att)
        await db.flush()
        await db.commit()
        await db.refresh(att)
        return att

    @classmethod
    async def list_attendances(
        cls, db: AsyncSession, mine_id: Optional[str] = None, worker_id: Optional[str] = None, shift: Optional[str] = None
    ) -> List[WorkerAttendance]:
        stmt = select(WorkerAttendance).where(WorkerAttendance.is_deleted == False)

        if mine_id:
            stmt = stmt.where(WorkerAttendance.mine_id == mine_id)
        if worker_id:
            stmt = stmt.where(WorkerAttendance.worker_id == worker_id)
        if shift:
            stmt = stmt.where(WorkerAttendance.shift == shift)

        stmt = stmt.order_by(WorkerAttendance.check_in.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ TRAINING MANAGEMENT ------------------

    @classmethod
    async def assign_training(
        cls, db: AsyncSession, worker_id: str, payload: WorkerTrainingCreate, user_id: Optional[str] = None
    ) -> WorkerTraining:
        worker = await cls.get_worker(db, worker_id)

        today = date.today()
        status_val = payload.status
        if payload.expiry_date < today:
            status_val = "EXPIRED"

        tr = WorkerTraining(
            id=generate_uuid(),
            worker_id=worker.id,
            program_name=payload.program_name,
            trainer_name=payload.trainer_name,
            completed_date=payload.completed_date,
            expiry_date=payload.expiry_date,
            status=status_val
        )
        db.add(tr)
        await db.flush()

        # Trigger alert if expired or pending
        if status_val in ["EXPIRED", "PENDING"]:
            alert = Alert(
                id=generate_uuid(),
                mine_id=worker.mine_id,
                zone_id="",
                title=f"Worker Training Alert: {worker.full_name} ({worker.employee_id})",
                message=f"Training program '{payload.program_name}' is {status_val.lower()} (Expiry: {payload.expiry_date}).",
                alert_type="TRAINING_ALERT",
                severity="HIGH" if status_val == "EXPIRED" else "MEDIUM",
                channel="IN_APP",
                target_role="SAFETY_OFFICER",
                status="PENDING"
            )
            db.add(alert)

        await db.commit()
        await db.refresh(tr)
        return tr

    @classmethod
    async def list_trainings(cls, db: AsyncSession, worker_id: Optional[str] = None) -> List[WorkerTraining]:
        stmt = select(WorkerTraining).where(WorkerTraining.is_deleted == False)
        if worker_id:
            stmt = stmt.where(WorkerTraining.worker_id == worker_id)
        stmt = stmt.order_by(WorkerTraining.expiry_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ CERTIFICATION MANAGEMENT ------------------

    @classmethod
    async def register_certification(
        cls, db: AsyncSession, worker_id: str, payload: WorkerCertificationCreate, user_id: Optional[str] = None
    ) -> WorkerCertification:
        worker = await cls.get_worker(db, worker_id)

        # Check duplicate certificate number
        stmt = select(WorkerCertification).where(
            and_(WorkerCertification.certificate_number == payload.certificate_number, WorkerCertification.is_deleted == False)
        )
        res = await db.execute(stmt)
        if res.scalars().first():
            raise DuplicateEntityError("WorkerCertification", "certificate_number", payload.certificate_number)

        today = date.today()
        v_status = payload.verification_status
        if payload.expiry_date < today:
            v_status = "EXPIRED"

        cert = WorkerCertification(
            id=generate_uuid(),
            worker_id=worker.id,
            certificate_name=payload.certificate_name,
            certificate_number=payload.certificate_number,
            issuing_authority=payload.issuing_authority,
            file_path=payload.file_path,
            valid_from=payload.valid_from,
            expiry_date=payload.expiry_date,
            verification_status=v_status
        )
        db.add(cert)
        await db.flush()

        # Trigger certification alert if expiring within 30 days or expired
        if payload.expiry_date <= today + timedelta(days=30):
            days_left = (payload.expiry_date - today).days
            alert = Alert(
                id=generate_uuid(),
                mine_id=worker.mine_id,
                zone_id="",
                title=f"Worker Certification Expiry Alert: {worker.full_name}",
                message=f"Statutory Certification '{payload.certificate_name}' ({payload.certificate_number}) expires in {days_left} days.",
                alert_type="CERTIFICATION_ALERT",
                severity="HIGH" if days_left <= 7 else "MEDIUM",
                channel="IN_APP",
                target_role="SAFETY_OFFICER",
                status="PENDING"
            )
            db.add(alert)

        await db.commit()
        await db.refresh(cert)
        return cert

    @classmethod
    async def list_certifications(cls, db: AsyncSession, worker_id: Optional[str] = None) -> List[WorkerCertification]:
        stmt = select(WorkerCertification).where(WorkerCertification.is_deleted == False)
        if worker_id:
            stmt = stmt.where(WorkerCertification.worker_id == worker_id)
        stmt = stmt.order_by(WorkerCertification.expiry_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ PPE ELIGIBILITY MANAGEMENT ------------------

    @classmethod
    async def assign_ppe(
        cls, db: AsyncSession, worker_id: str, payload: WorkerPPECreate, user_id: Optional[str] = None
    ) -> WorkerPPE:
        worker = await cls.get_worker(db, worker_id)

        today = date.today()
        comp_status = payload.compliance_status
        if payload.expiry_date < today:
            comp_status = "EXPIRED"

        ppe = WorkerPPE(
            id=generate_uuid(),
            worker_id=worker.id,
            item_type=payload.item_type,
            issuance_date=payload.issuance_date,
            expiry_date=payload.expiry_date,
            compliance_status=comp_status,
            remarks=payload.remarks
        )
        db.add(ppe)
        await db.flush()

        if comp_status in ["EXPIRED", "REPLACEMENT_REQUIRED"]:
            alert = Alert(
                id=generate_uuid(),
                mine_id=worker.mine_id,
                zone_id="",
                title=f"PPE Compliance Warning: {worker.full_name}",
                message=f"PPE Item '{payload.item_type}' is {comp_status.lower()}. Immediate replacement required.",
                alert_type="PPE_ALERT",
                severity="HIGH",
                channel="IN_APP",
                target_role="SAFETY_OFFICER",
                status="PENDING"
            )
            db.add(alert)

        await db.commit()
        await db.refresh(ppe)
        return ppe

    @classmethod
    async def list_ppes(cls, db: AsyncSession, worker_id: Optional[str] = None) -> List[WorkerPPE]:
        stmt = select(WorkerPPE).where(WorkerPPE.is_deleted == False)
        if worker_id:
            stmt = stmt.where(WorkerPPE.worker_id == worker_id)
        stmt = stmt.order_by(WorkerPPE.expiry_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ WORK AUTHORIZATION ------------------

    @classmethod
    async def grant_authorization(
        cls, db: AsyncSession, worker_id: str, payload: WorkerAuthorizationCreate, user_id: Optional[str] = None
    ) -> WorkerAuthorization:
        worker = await cls.get_worker(db, worker_id)

        today = date.today()
        status_val = payload.status
        if payload.expiry_date < today:
            status_val = "EXPIRED"

        auth = WorkerAuthorization(
            id=generate_uuid(),
            worker_id=worker.id,
            zone_id=payload.zone_id,
            permit_type=payload.permit_type,
            grant_date=payload.grant_date,
            expiry_date=payload.expiry_date,
            status=status_val,
            granted_by=payload.granted_by
        )
        db.add(auth)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="WORKER_AUTHORIZATION_GRANTED",
            entity_type="WorkerAuthorization",
            entity_id=auth.id,
            changes={"permit_type": payload.permit_type, "zone_id": payload.zone_id},
            user_id=user_id,
            mine_id=worker.mine_id
        )
        await db.commit()
        await db.refresh(auth)
        return auth

    @classmethod
    async def revoke_authorization(
        cls, db: AsyncSession, authorization_id: str, user_id: Optional[str] = None
    ) -> WorkerAuthorization:
        stmt = select(WorkerAuthorization).where(
            and_(WorkerAuthorization.id == authorization_id, WorkerAuthorization.is_deleted == False)
        )
        res = await db.execute(stmt)
        auth = res.scalars().first()
        if not auth:
            raise EntityNotFoundError("WorkerAuthorization", authorization_id)

        auth.status = "REVOKED"
        auth.updated_at = utc_now()

        # Trigger authorization alert
        stmt_w = select(Worker).where(Worker.id == auth.worker_id)
        res_w = await db.execute(stmt_w)
        worker = res_w.scalars().first()

        if worker:
            alert = Alert(
                id=generate_uuid(),
                mine_id=worker.mine_id,
                zone_id=auth.zone_id,
                title=f"Work Permit Revoked: {worker.full_name}",
                message=f"Work authorization for permit '{auth.permit_type}' in zone '{auth.zone_id}' has been REVOKED.",
                alert_type="AUTHORIZATION_ALERT",
                severity="CRITICAL",
                channel="IN_APP",
                target_role="SAFETY_OFFICER",
                status="PENDING"
            )
            db.add(alert)

        await db.commit()
        await db.refresh(auth)
        return auth

    @classmethod
    async def list_authorizations(cls, db: AsyncSession, worker_id: Optional[str] = None) -> List[WorkerAuthorization]:
        stmt = select(WorkerAuthorization).where(WorkerAuthorization.is_deleted == False)
        if worker_id:
            stmt = stmt.where(WorkerAuthorization.worker_id == worker_id)
        stmt = stmt.order_by(WorkerAuthorization.expiry_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ DASHBOARD & REPORTS METRICS ------------------

    @classmethod
    async def get_dashboard_stats(cls, db: AsyncSession, mine_id: Optional[str] = None) -> WorkerDashboardStats:
        workers = await cls.list_workers(db, mine_id=mine_id)
        total = len(workers)
        active = sum(1 for w in workers if w.status == "ACTIVE")
        inactive = sum(1 for w in workers if w.status == "INACTIVE")
        suspended = sum(1 for w in workers if w.status == "SUSPENDED")
        unauthorized = sum(1 for w in workers if w.status == "UNAUTHORIZED")

        pending_trainings = 0
        expired_certs = 0
        total_ppe_items = 0
        compliant_ppe = 0
        total_auths = 0
        granted_auths = 0

        today = date.today()

        for w in workers:
            pending_trainings += sum(1 for t in (w.trainings or []) if t.status in ["PENDING", "EXPIRED"] or t.expiry_date < today)
            expired_certs += sum(1 for c in (w.certifications or []) if c.verification_status == "EXPIRED" or c.expiry_date < today)
            
            for p in (w.ppes or []):
                total_ppe_items += 1
                if p.compliance_status == "COMPLIANT" and p.expiry_date >= today:
                    compliant_ppe += 1

            for a in (w.authorizations or []):
                total_auths += 1
                if a.status == "GRANTED" and a.expiry_date >= today:
                    granted_auths += 1

        ppe_pct = round((compliant_ppe / total_ppe_items * 100), 1) if total_ppe_items > 0 else 100.0
        auth_pct = round((granted_auths / total_auths * 100), 1) if total_auths > 0 else 100.0

        return WorkerDashboardStats(
            total_workers=total,
            active_workers=active,
            inactive_workers=inactive,
            suspended_workers=suspended,
            unauthorized_workers=unauthorized,
            workers_pending_training=pending_trainings,
            expired_certifications_count=expired_certs,
            ppe_compliance_percent=ppe_pct,
            authorization_compliance_percent=auth_pct
        )

    @classmethod
    async def get_reports_summary(cls, db: AsyncSession, mine_id: Optional[str] = None) -> WorkerReportsSummary:
        attendances = await cls.list_attendances(db, mine_id=mine_id)
        trainings = await cls.list_trainings(db)
        certifications = await cls.list_certifications(db)
        ppes = await cls.list_ppes(db)
        authorizations = await cls.list_authorizations(db)

        today = date.today()

        present_count = sum(1 for a in attendances if a.status in ["PRESENT", "OVERTIME"])
        absent_count = sum(1 for a in attendances if a.status == "ABSENT")

        active_certs = sum(1 for c in certifications if c.verification_status == "VERIFIED" and c.expiry_date >= today)
        expiring_certs_30d = sum(1 for c in certifications if today <= c.expiry_date <= today + timedelta(days=30))

        trainings_completed = sum(1 for t in trainings if t.status == "COMPLETED")
        pending_trainings = sum(1 for t in trainings if t.status == "PENDING" or t.expiry_date < today)

        compliant_ppe = sum(1 for p in ppes if p.compliance_status == "COMPLIANT")
        replacement_needed_ppe = sum(1 for p in ppes if p.compliance_status in ["REPLACEMENT_REQUIRED", "EXPIRED"])

        active_permits = sum(1 for a in authorizations if a.status == "GRANTED" and a.expiry_date >= today)
        revoked_permits = sum(1 for a in authorizations if a.status == "REVOKED")

        return WorkerReportsSummary(
            total_attendances_today=len(attendances),
            present_today_count=present_count,
            absent_today_count=absent_count,
            total_active_certifications=active_certs,
            expiring_certifications_30d=expiring_certs_30d,
            total_trainings_completed=trainings_completed,
            pending_trainings_count=pending_trainings,
            compliant_ppe_items_count=compliant_ppe,
            replacement_needed_ppe_count=replacement_needed_ppe,
            active_permits_count=active_permits,
            revoked_permits_count=revoked_permits
        )

    @classmethod
    async def get_worker_by_email(cls, db: AsyncSession, email: str) -> Optional[Worker]:
        stmt = (
            select(Worker)
            .where(and_(Worker.email == email, Worker.is_deleted == False))
            .options(
                selectinload(Worker.attendances),
                selectinload(Worker.trainings),
                selectinload(Worker.certifications),
                selectinload(Worker.ppes),
                selectinload(Worker.authorizations),
                selectinload(Worker.insurances),
                selectinload(Worker.leaves)
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def create_insurance(
        cls, db: AsyncSession, worker_id: str, payload: WorkerInsuranceCreate, user_id: Optional[str] = None
    ) -> WorkerInsurance:
        worker = await cls.get_worker(db, worker_id)
        insurance = WorkerInsurance(
            id=generate_uuid(),
            worker_id=worker.id,
            policy_provider=payload.policy_provider,
            policy_number=payload.policy_number,
            policy_type=payload.policy_type,
            coverage_amount=payload.coverage_amount,
            start_date=payload.start_date,
            expiry_date=payload.expiry_date,
            nominee_name=payload.nominee_name,
            nominee_relation=payload.nominee_relation,
            premium_status=payload.premium_status,
            tpa_contact_number=payload.tpa_contact_number
        )
        db.add(insurance)
        await db.flush()

        await audit_service.log_action(
            db=db, user_id=user_id, action="INSURANCE_ASSIGNED",
            entity_type="WORKER_INSURANCE", entity_id=insurance.id,
            details={"worker_id": worker_id, "policy_number": payload.policy_number}
        )
        return insurance

    @classmethod
    async def list_insurances(
        cls, db: AsyncSession, worker_id: Optional[str] = None
    ) -> List[WorkerInsurance]:
        query = select(WorkerInsurance).where(WorkerInsurance.is_deleted == False)
        if worker_id:
            query = query.where(WorkerInsurance.worker_id == worker_id)
        query = query.order_by(WorkerInsurance.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def apply_leave(
        cls, db: AsyncSession, worker_id: str, payload: WorkerLeaveCreate, user_id: Optional[str] = None
    ) -> WorkerLeave:
        worker = await cls.get_worker(db, worker_id)
        leave = WorkerLeave(
            id=generate_uuid(),
            worker_id=worker.id,
            mine_id=worker.mine_id,
            leave_type=payload.leave_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            days_count=payload.days_count,
            reason=payload.reason,
            status="PENDING"
        )
        db.add(leave)
        await db.flush()

        await audit_service.log_action(
            db=db, user_id=user_id, action="LEAVE_APPLIED",
            entity_type="WORKER_LEAVE", entity_id=leave.id,
            details={"worker_id": worker_id, "days": payload.days_count, "type": payload.leave_type}
        )
        return leave

    @classmethod
    async def list_leaves(
        cls, db: AsyncSession, worker_id: Optional[str] = None, mine_id: Optional[str] = None
    ) -> List[WorkerLeave]:
        query = select(WorkerLeave).where(WorkerLeave.is_deleted == False)
        if worker_id:
            query = query.where(WorkerLeave.worker_id == worker_id)
        if mine_id:
            query = query.where(WorkerLeave.mine_id == mine_id)
        query = query.order_by(WorkerLeave.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def action_leave(
        cls, db: AsyncSession, leave_id: str, payload: WorkerLeaveAction, approver_name: str
    ) -> WorkerLeave:
        stmt = select(WorkerLeave).where(and_(WorkerLeave.id == leave_id, WorkerLeave.is_deleted == False))
        res = await db.execute(stmt)
        leave = res.scalars().first()
        if not leave:
            raise EntityNotFoundError("WorkerLeave", leave_id)

        leave.status = payload.status
        leave.approved_by = approver_name
        leave.supervisor_remarks = payload.supervisor_remarks
        await db.flush()
        return leave


worker_service = WorkerService()

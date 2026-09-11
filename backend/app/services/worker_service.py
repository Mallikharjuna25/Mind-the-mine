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
    WorkerAuthorization, WorkerInsurance, WorkerLeave,
    WorkerPass, WorkerDocument, WorkerInduction
)
from app.models.workflow_models import Alert
from app.schemas.worker_schemas import (
    WorkerCreate, WorkerUpdate, WorkerAttendanceCreate, WorkerTrainingCreate,
    WorkerCertificationCreate, WorkerPPECreate, WorkerAuthorizationCreate,
    WorkerInsuranceCreate, WorkerLeaveCreate, WorkerLeaveAction,
    WorkerPassCreate, WorkerPassAction, WorkerPassResponse,
    WorkerDocumentResponse, WorkerDocumentReviewAction,
    WorkerInductionCreate, WorkerInductionResponse, WorkerInductionStats,
    WorkerZoneClearanceResponse,
    WorkerDashboardStats, WorkerReportsSummary
)
from app.services.audit_service import audit_service
from app.ai.ocr.ocr_engine import ocr_engine


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
            selectinload(Worker.authorizations),
            selectinload(Worker.insurances),
            selectinload(Worker.leaves),
            selectinload(Worker.passes),
            selectinload(Worker.documents),
            selectinload(Worker.inductions)
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
            selectinload(Worker.authorizations),
            selectinload(Worker.insurances),
            selectinload(Worker.leaves),
            selectinload(Worker.passes),
            selectinload(Worker.documents),
            selectinload(Worker.inductions)
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

    # ------------------ RFID PASS LIFECYCLE ------------------

    @classmethod
    async def register_pass(
        cls, db: AsyncSession, worker_id: str, payload: WorkerPassCreate, issued_by: str
    ) -> WorkerPass:
        worker = await cls.get_worker(db, worker_id)

        # Rule: Never allow two active workers to have the same RFID UID
        stmt = select(WorkerPass).where(
            and_(
                WorkerPass.rfid_uid == payload.rfid_uid,
                WorkerPass.status == "ACTIVE",
                WorkerPass.is_deleted == False
            )
        )
        res = await db.execute(stmt)
        active_pass = res.scalars().first()
        if active_pass:
            raise DuplicateEntityError(
                "WorkerPass", "rfid_uid", f"{payload.rfid_uid} (Already assigned to active worker pass {active_pass.pass_number})"
            )

        pass_num = payload.pass_number or f"PASS-{worker.employee_id}-{generate_uuid()[:6].upper()}"
        issue_d = payload.issue_date or date.today()
        expiry_d = payload.expiry_date or (date.today() + timedelta(days=365))

        new_pass = WorkerPass(
            id=generate_uuid(),
            worker_id=worker.id,
            mine_id=worker.mine_id,
            rfid_uid=payload.rfid_uid,
            pass_number=pass_num,
            issue_date=issue_d,
            expiry_date=expiry_d,
            status="ACTIVE",
            access_level=payload.access_level,
            permitted_zones=payload.permitted_zones,
            issued_by=issued_by
        )
        db.add(new_pass)
        worker.rfid_tag = payload.rfid_uid
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="RFID_PASS_ISSUED",
            entity_type="WorkerPass",
            entity_id=new_pass.id,
            changes={"pass_number": pass_num, "rfid_uid": payload.rfid_uid, "access_level": payload.access_level},
            user_id=issued_by,
            mine_id=worker.mine_id
        )
        await db.commit()
        await db.refresh(new_pass)
        return new_pass

    @classmethod
    async def action_pass(
        cls, db: AsyncSession, pass_id: str, payload: WorkerPassAction, actor: str
    ) -> WorkerPass:
        stmt = select(WorkerPass).where(and_(WorkerPass.id == pass_id, WorkerPass.is_deleted == False))
        res = await db.execute(stmt)
        pass_obj = res.scalars().first()
        if not pass_obj:
            raise EntityNotFoundError("WorkerPass", pass_id)

        old_status = pass_obj.status
        action_upper = payload.action.upper()

        if action_upper in ("REVOKE", "BLOCK", "SUSPEND"):
            pass_obj.status = "REVOKED" if action_upper == "REVOKE" else ("SUSPENDED" if action_upper == "SUSPEND" else "BLOCKED")
            pass_obj.revoked_by = actor
            pass_obj.revocation_reason = payload.revocation_reason or f"Action {action_upper} triggered by authorized officer."
        elif action_upper == "RENEW":
            pass_obj.status = "ACTIVE"
            pass_obj.expiry_date = payload.new_expiry_date or (date.today() + timedelta(days=365))
        elif action_upper == "REPLACE":
            if not payload.new_rfid_uid:
                raise ValueError("New RFID UID is required for pass replacement.")
            # Verify uniqueness of new RFID
            check_stmt = select(WorkerPass).where(
                and_(WorkerPass.rfid_uid == payload.new_rfid_uid, WorkerPass.status == "ACTIVE", WorkerPass.is_deleted == False)
            )
            c_res = await db.execute(check_stmt)
            if c_res.scalars().first():
                raise DuplicateEntityError("WorkerPass", "rfid_uid", payload.new_rfid_uid)

            pass_obj.status = "REVOKED"
            pass_obj.revocation_reason = f"Replaced by new RFID card {payload.new_rfid_uid}"
            pass_obj.revoked_by = actor

            # Create replacement pass
            new_pass = WorkerPass(
                id=generate_uuid(),
                worker_id=pass_obj.worker_id,
                mine_id=pass_obj.mine_id,
                rfid_uid=payload.new_rfid_uid,
                pass_number=f"{pass_obj.pass_number}-R",
                issue_date=date.today(),
                expiry_date=payload.new_expiry_date or (date.today() + timedelta(days=365)),
                status="ACTIVE",
                access_level=pass_obj.access_level,
                permitted_zones=pass_obj.permitted_zones,
                issued_by=actor
            )
            db.add(new_pass)
            # Update worker's tag
            w_stmt = select(Worker).where(Worker.id == pass_obj.worker_id)
            w_res = await db.execute(w_stmt)
            w = w_res.scalars().first()
            if w:
                w.rfid_tag = payload.new_rfid_uid

        await db.flush()
        await audit_service.log_action(
            db=db,
            action="RFID_PASS_STATUS_CHANGED",
            entity_type="WorkerPass",
            entity_id=pass_obj.id,
            changes={"previous_status": old_status, "new_status": pass_obj.status, "action": action_upper},
            user_id=actor,
            mine_id=pass_obj.mine_id
        )
        await db.commit()
        await db.refresh(pass_obj)
        return pass_obj

    @classmethod
    async def list_passes(
        cls, db: AsyncSession, worker_id: Optional[str] = None, mine_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[WorkerPass]:
        query = select(WorkerPass).where(WorkerPass.is_deleted == False)
        if worker_id:
            query = query.where(WorkerPass.worker_id == worker_id)
        if mine_id:
            query = query.where(WorkerPass.mine_id == mine_id)
        if status:
            query = query.where(WorkerPass.status == status)
        query = query.order_by(WorkerPass.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    # ------------------ WORKER DOCUMENTS & OCR PIPELINE ------------------

    @classmethod
    async def upload_worker_document(
        cls,
        db: AsyncSession,
        worker_id: Optional[str],
        contractor_id: Optional[str],
        document_type: str,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        mime_type: str,
        user_id: Optional[str] = None
    ) -> WorkerDocument:
        expected_worker_name = None
        if worker_id:
            w_stmt = select(Worker).where(Worker.id == worker_id)
            w_res = await db.execute(w_stmt)
            w = w_res.scalars().first()
            if w:
                expected_worker_name = w.full_name

        # Execute Multi-Tier OCR + Field Extraction + Confidence Validation
        raw_text, extracted_data, confs, overall_conf, ocr_status, errors = ocr_engine.process_workforce_document(
            file_path=file_path,
            document_type=document_type,
            expected_worker_name=expected_worker_name
        )

        doc_num = extracted_data.get("document_number") or extracted_data.get("certificate_number") or extracted_data.get("registration_number")
        iss_str = extracted_data.get("issue_date") or extracted_data.get("exam_date") or extracted_data.get("training_date")
        exp_str = extracted_data.get("expiry_date")

        issue_d = None
        if iss_str:
            try:
                issue_d = datetime.strptime(iss_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        expiry_d = None
        if exp_str:
            try:
                expiry_d = datetime.strptime(exp_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        doc = WorkerDocument(
            id=generate_uuid(),
            worker_id=worker_id,
            contractor_id=contractor_id,
            document_type=document_type,
            document_number=str(doc_num) if doc_num else None,
            issue_date=issue_d,
            expiry_date=expiry_d,
            file_path=file_path,
            original_filename=file_name,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            ocr_status=ocr_status,
            ocr_confidence=overall_conf,
            raw_ocr_text=raw_text,
            extracted_data=extracted_data,
            validation_errors=errors if errors else None,
            verification_status="VERIFIED" if ocr_status == "AUTO_ACCEPTED" else "PENDING",
            verified_by=user_id if ocr_status == "AUTO_ACCEPTED" else None,
            verified_at=utc_now() if ocr_status == "AUTO_ACCEPTED" else None
        )
        db.add(doc)
        await db.flush()

        # If auto-accepted, propagate statutory health or induction updates
        if ocr_status == "AUTO_ACCEPTED" and worker_id:
            w_stmt = select(Worker).where(Worker.id == worker_id)
            w_res = await db.execute(w_stmt)
            worker_rec = w_res.scalars().first()
            if worker_rec:
                if "FITNESS" in document_type.upper() or "MEDICAL" in document_type.upper():
                    worker_rec.medical_fitness_status = extracted_data.get("fitness_status", "FIT")
                    worker_rec.medical_exam_date = issue_d
                    worker_rec.medical_expiry_date = expiry_d
                elif "INDUCTION" in document_type.upper() or "TRAINING" in document_type.upper():
                    # Create induction record automatically
                    induction = WorkerInduction(
                        id=generate_uuid(),
                        worker_id=worker_id,
                        mine_id=worker_rec.mine_id,
                        induction_type="INITIAL_STATUTORY",
                        training_title=extracted_data.get("training_title", "DGMS Statutory Induction"),
                        trainer_name=extracted_data.get("trainer_name", "DGMS Instructor"),
                        training_date=issue_d or date.today(),
                        validity_months=12,
                        expiry_date=expiry_d or (date.today() + timedelta(days=365)),
                        score_percent=extracted_data.get("score_percent", 90.0),
                        certificate_document_id=doc.id,
                        verification_status="VERIFIED",
                        status="COMPLETED"
                    )
                    db.add(induction)

        await audit_service.log_action(
            db=db,
            action="WORKER_DOCUMENT_UPLOADED_OCR",
            entity_type="WorkerDocument",
            entity_id=doc.id,
            changes={"document_type": document_type, "ocr_confidence": overall_conf, "ocr_status": ocr_status},
            user_id=user_id,
            mine_id=None
        )
        await db.commit()
        await db.refresh(doc)
        return doc

    @classmethod
    async def review_worker_document(
        cls, db: AsyncSession, document_id: str, payload: WorkerDocumentReviewAction, reviewer: str
    ) -> WorkerDocument:
        stmt = select(WorkerDocument).where(and_(WorkerDocument.id == document_id, WorkerDocument.is_deleted == False))
        res = await db.execute(stmt)
        doc = res.scalars().first()
        if not doc:
            raise EntityNotFoundError("WorkerDocument", document_id)

        old_data = doc.extracted_data or {}
        decision_upper = payload.decision.upper()

        if decision_upper in ("APPROVE", "EDIT_AND_APPROVE"):
            doc.verification_status = "VERIFIED"
            doc.verified_by = reviewer
            doc.verified_at = utc_now()
            doc.ocr_status = "VERIFIED"
            if payload.corrected_data:
                doc.extracted_data = payload.corrected_data
                # Update issue/expiry if provided in corrected_data
                if "issue_date" in payload.corrected_data:
                    try:
                        doc.issue_date = datetime.strptime(payload.corrected_data["issue_date"], "%Y-%m-%d").date()
                    except Exception:
                        pass
                if "expiry_date" in payload.corrected_data:
                    try:
                        doc.expiry_date = datetime.strptime(payload.corrected_data["expiry_date"], "%Y-%m-%d").date()
                    except Exception:
                        pass

            # Update related worker fitness if applicable
            if doc.worker_id and ("FITNESS" in doc.document_type.upper() or "MEDICAL" in doc.document_type.upper()):
                w_stmt = select(Worker).where(Worker.id == doc.worker_id)
                w_res = await db.execute(w_stmt)
                w = w_res.scalars().first()
                if w:
                    w.medical_fitness_status = doc.extracted_data.get("fitness_status", "FIT")
                    w.medical_exam_date = doc.issue_date
                    w.medical_expiry_date = doc.expiry_date

        elif decision_upper == "REJECT":
            doc.verification_status = "REJECTED"
            doc.ocr_status = "REJECTED"
            doc.rejection_reason = payload.rejection_reason or "Document rejected by reviewing officer."

        await db.flush()
        await audit_service.log_action(
            db=db,
            action="WORKER_DOCUMENT_REVIEWED",
            entity_type="WorkerDocument",
            entity_id=doc.id,
            changes={
                "decision": decision_upper,
                "original_data": old_data,
                "final_data": doc.extracted_data,
                "reviewer": reviewer
            },
            user_id=reviewer,
            mine_id=None
        )
        await db.commit()
        await db.refresh(doc)
        return doc

    @classmethod
    async def list_worker_documents(
        cls,
        db: AsyncSession,
        worker_id: Optional[str] = None,
        contractor_id: Optional[str] = None,
        verification_status: Optional[str] = None
    ) -> List[WorkerDocument]:
        query = select(WorkerDocument).where(WorkerDocument.is_deleted == False)
        if worker_id:
            query = query.where(WorkerDocument.worker_id == worker_id)
        if contractor_id:
            query = query.where(WorkerDocument.contractor_id == contractor_id)
        if verification_status:
            query = query.where(WorkerDocument.verification_status == verification_status)
        query = query.order_by(WorkerDocument.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    # ------------------ DGMS SAFETY INDUCTION WORKFLOW ------------------

    @classmethod
    async def create_induction(
        cls, db: AsyncSession, worker_id: str, payload: WorkerInductionCreate, user_id: Optional[str] = None
    ) -> WorkerInduction:
        worker = await cls.get_worker(db, worker_id)
        exp_date = payload.training_date + timedelta(days=payload.validity_months * 30)

        induction = WorkerInduction(
            id=generate_uuid(),
            worker_id=worker.id,
            mine_id=worker.mine_id,
            induction_type=payload.induction_type,
            training_title=payload.training_title,
            trainer_name=payload.trainer_name,
            training_date=payload.training_date,
            validity_months=payload.validity_months,
            expiry_date=exp_date,
            score_percent=payload.score_percent,
            verification_status="VERIFIED",
            status="COMPLETED",
            remarks=payload.remarks
        )
        db.add(induction)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="WORKER_INDUCTION_COMPLETED",
            entity_type="WorkerInduction",
            entity_id=induction.id,
            changes={"training_title": payload.training_title, "expiry_date": exp_date.isoformat()},
            user_id=user_id,
            mine_id=worker.mine_id
        )
        await db.commit()
        await db.refresh(induction)
        return induction

    @classmethod
    async def list_inductions(
        cls, db: AsyncSession, worker_id: Optional[str] = None, mine_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[WorkerInduction]:
        query = select(WorkerInduction).where(WorkerInduction.is_deleted == False)
        if worker_id:
            query = query.where(WorkerInduction.worker_id == worker_id)
        if mine_id:
            query = query.where(WorkerInduction.mine_id == mine_id)
        if status:
            query = query.where(WorkerInduction.status == status)
        query = query.order_by(WorkerInduction.training_date.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def get_induction_stats(cls, db: AsyncSession, mine_id: Optional[str] = None) -> WorkerInductionStats:
        w_stmt = select(func.count(Worker.id)).where(Worker.is_deleted == False)
        if mine_id:
            w_stmt = w_stmt.where(Worker.mine_id == mine_id)
        total_w = (await db.execute(w_stmt)).scalar() or 0

        today = date.today()
        soon_threshold = today + timedelta(days=30)

        # Inductions
        i_stmt = select(WorkerInduction).where(WorkerInduction.is_deleted == False)
        if mine_id:
            i_stmt = i_stmt.where(WorkerInduction.mine_id == mine_id)
        all_ind = (await db.execute(i_stmt)).scalars().all()

        inducted_workers = set()
        expired_count = 0
        expiring_soon_count = 0

        for ind in all_ind:
            if ind.expiry_date < today:
                expired_count += 1
            elif ind.expiry_date <= soon_threshold:
                expiring_soon_count += 1
                inducted_workers.add(ind.worker_id)
            else:
                inducted_workers.add(ind.worker_id)

        inducted_count = len(inducted_workers)
        pending_induction_count = max(0, total_w - inducted_count)

        return WorkerInductionStats(
            total_workers=total_w,
            inducted_count=inducted_count,
            pending_induction_count=pending_induction_count,
            expiring_soon_count=expiring_soon_count,
            expired_count=expired_count,
            safety_cleared_count=inducted_count
        )

    # ------------------ ZONE ACCESS CLEARANCE ENGINE ------------------

    @classmethod
    async def check_zone_clearance(
        cls, db: AsyncSession, worker_id: str, zone_id: str
    ) -> WorkerZoneClearanceResponse:
        """
        Derives access eligibility deterministically:
        Access Eligible = (Worker Active) AND (Active RFID Pass) AND (Valid DGMS Induction) AND (PPE Compliant) AND (Zone Authorized)
        """
        worker = await cls.get_worker(db, worker_id)
        today = date.today()

        blocking_reasons: List[str] = []

        # 1. Worker Status
        is_worker_active = worker.status == "ACTIVE"
        if not is_worker_active:
            blocking_reasons.append(f"Worker status is {worker.status} (Must be ACTIVE)")

        # 2. Active RFID Pass
        active_pass = None
        for p in worker.passes:
            if p.status == "ACTIVE" and p.expiry_date >= today:
                active_pass = p
                break
        has_active_pass = active_pass is not None
        if not has_active_pass:
            blocking_reasons.append("No active, unexpired RFID access pass issued to worker.")

        # 3. Valid DGMS Induction
        has_valid_induction = False
        for ind in worker.inductions:
            if ind.status == "COMPLETED" and ind.expiry_date >= today and ind.verification_status == "VERIFIED":
                has_valid_induction = True
                break
        # Fallback check on worker.trainings
        if not has_valid_induction:
            for tr in worker.trainings:
                if tr.status == "COMPLETED" and tr.expiry_date >= today:
                    has_valid_induction = True
                    break
        if not has_valid_induction:
            blocking_reasons.append("Mandatory DGMS Safety Induction training is expired or incomplete.")

        # 4. PPE Compliance
        ppe_compliant = True
        for ppe in worker.ppes:
            if ppe.compliance_status in ("EXPIRED", "REPLACEMENT_REQUIRED"):
                ppe_compliant = False
                blocking_reasons.append(f"PPE item '{ppe.item_type}' requires replacement/is non-compliant.")
                break

        # 5. Zone Authorization
        zone_authorized = False
        if zone_id in ("ZONE-GENERAL", "SURFACE_YARD", "GENERAL_SURFACE"):
            zone_authorized = True
        else:
            # Check pass permitted zones
            if active_pass and (zone_id in active_pass.permitted_zones or active_pass.access_level == "ALL_ZONES"):
                zone_authorized = True
            # Check worker authorizations
            for auth in worker.authorizations:
                if auth.zone_id == zone_id and auth.status == "GRANTED" and auth.expiry_date >= today:
                    zone_authorized = True
                    break

        if not zone_authorized:
            blocking_reasons.append(f"Worker is not explicitly authorized for restricted zone '{zone_id}'.")

        is_eligible = (
            is_worker_active and has_active_pass and has_valid_induction and ppe_compliant and zone_authorized
        )
        clearance_status = "CLEARED" if is_eligible else ("BLOCKED" if not is_worker_active or not has_active_pass else "RESTRICTED")

        return WorkerZoneClearanceResponse(
            worker_id=worker.id,
            worker_name=worker.full_name,
            zone_id=zone_id,
            zone_name=f"Mine Zone {zone_id}",
            is_access_eligible=is_eligible,
            clearance_status=clearance_status,
            checks={
                "worker_active": is_worker_active,
                "active_rfid_pass": has_active_pass,
                "rfid_uid": active_pass.rfid_uid if active_pass else None,
                "induction_valid": has_valid_induction,
                "ppe_compliant": ppe_compliant,
                "zone_authorized": zone_authorized
            },
            blocking_reasons=blocking_reasons
        )


worker_service = WorkerService()

"""
Contractor Management Service
Orchestrates Contractor Lifecycle, Contracts, Document Management, Compliance & Performance Scoring,
Contract Renewals, and Automated Alerts.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, DuplicateEntityError, InvalidStateTransitionError
from app.core.logging_config import logger
from app.models.base import generate_uuid, utc_now
from app.models.contractor_models import (
    Contractor, Contract, ContractDocument, ContractCompliance, ContractPerformance
)
from app.models.workflow_models import Alert
from app.schemas.contractor_schemas import (
    ContractorCreate, ContractorUpdate, ContractCreate, ContractUpdate,
    ContractRenewalRequest, ContractComplianceCreate, ContractPerformanceCreate,
    ContractorDashboardStats
)
from app.services.audit_service import audit_service


class ContractorService:

    @classmethod
    async def create_contractor(
        cls, db: AsyncSession, payload: ContractorCreate, user_id: Optional[str] = None
    ) -> Contractor:
        # Check duplicate registration number
        stmt = select(Contractor).where(
            and_(
                Contractor.registration_number == payload.registration_number,
                Contractor.is_deleted == False
            )
        )
        res = await db.execute(stmt)
        if res.scalars().first():
            raise DuplicateEntityError("Contractor", "registration_number", payload.registration_number)

        contractor = Contractor(
            id=generate_uuid(),
            mine_id=payload.mine_id,
            company_name=payload.company_name,
            registration_number=payload.registration_number,
            contact_person=payload.contact_person,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
            work_scope=payload.work_scope,
            status=payload.status,
            compliance_score=100.0,
            compliance_status="COMPLIANT",
            performance_score=5.0
        )
        db.add(contractor)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="CONTRACTOR_CREATED",
            entity_type="Contractor",
            entity_id=contractor.id,
            changes={"company_name": contractor.company_name, "reg_no": contractor.registration_number},
            user_id=user_id,
            mine_id=payload.mine_id
        )
        await db.commit()
        await db.refresh(contractor)
        return contractor

    @classmethod
    async def get_contractor(cls, db: AsyncSession, contractor_id: str) -> Contractor:
        stmt = select(Contractor).where(
            and_(Contractor.id == contractor_id, Contractor.is_deleted == False)
        ).options(
            selectinload(Contractor.contracts),
            selectinload(Contractor.documents),
            selectinload(Contractor.compliances),
            selectinload(Contractor.performances)
        )
        res = await db.execute(stmt)
        contractor = res.scalars().first()
        if not contractor:
            raise EntityNotFoundError("Contractor", contractor_id)
        return contractor

    @classmethod
    async def list_contractors(
        cls,
        db: AsyncSession,
        mine_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        compliance_status: Optional[str] = None,
        work_scope: Optional[str] = None
    ) -> List[Contractor]:
        stmt = select(Contractor).where(Contractor.is_deleted == False).options(
            selectinload(Contractor.contracts),
            selectinload(Contractor.documents),
            selectinload(Contractor.compliances),
            selectinload(Contractor.performances)
        )

        if mine_id:
            stmt = stmt.where(Contractor.mine_id == mine_id)
        if status:
            stmt = stmt.where(Contractor.status == status)
        if compliance_status:
            stmt = stmt.where(Contractor.compliance_status == compliance_status)
        if work_scope:
            stmt = stmt.where(Contractor.work_scope == work_scope)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Contractor.company_name.ilike(search_pattern),
                    Contractor.registration_number.ilike(search_pattern),
                    Contractor.contact_person.ilike(search_pattern),
                    Contractor.work_scope.ilike(search_pattern)
                )
            )

        stmt = stmt.order_by(Contractor.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def update_contractor(
        cls, db: AsyncSession, contractor_id: str, payload: ContractorUpdate, user_id: Optional[str] = None
    ) -> Contractor:
        contractor = await cls.get_contractor(db, contractor_id)

        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            if val is not None:
                setattr(contractor, key, val)

        contractor.updated_at = utc_now()
        await audit_service.log_action(
            db=db,
            action="CONTRACTOR_UPDATED",
            entity_type="Contractor",
            entity_id=contractor.id,
            changes=update_data,
            user_id=user_id,
            mine_id=contractor.mine_id
        )
        await db.commit()
        await db.refresh(contractor)
        return contractor

    @classmethod
    async def delete_contractor(cls, db: AsyncSession, contractor_id: str, user_id: Optional[str] = None) -> bool:
        contractor = await cls.get_contractor(db, contractor_id)
        contractor.is_deleted = True
        contractor.status = "TERMINATED"
        contractor.updated_at = utc_now()

        await audit_service.log_action(
            db=db,
            action="CONTRACTOR_DELETED",
            entity_type="Contractor",
            entity_id=contractor.id,
            changes={"status": "TERMINATED", "is_deleted": True},
            user_id=user_id,
            mine_id=contractor.mine_id
        )
        await db.commit()
        return True

    # ------------------ CONTRACT MANAGEMENT ------------------

    @classmethod
    async def add_contract(
        cls, db: AsyncSession, contractor_id: str, payload: ContractCreate, user_id: Optional[str] = None
    ) -> Contract:
        contractor = await cls.get_contractor(db, contractor_id)

        # Check unique contract number
        stmt = select(Contract).where(
            and_(Contract.contract_number == payload.contract_number, Contract.is_deleted == False)
        )
        res = await db.execute(stmt)
        if res.scalars().first():
            raise DuplicateEntityError("Contract", "contract_number", payload.contract_number)

        contract = Contract(
            id=generate_uuid(),
            contractor_id=contractor.id,
            mine_id=payload.mine_id,
            contract_number=payload.contract_number,
            title=payload.title,
            contract_type=payload.contract_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            contract_value=payload.contract_value,
            status=payload.status,
            renewal_count=0
        )
        db.add(contract)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="CONTRACT_CREATED",
            entity_type="Contract",
            entity_id=contract.id,
            changes={"contract_number": contract.contract_number, "title": contract.title},
            user_id=user_id,
            mine_id=payload.mine_id
        )
        await db.commit()
        await db.refresh(contract)
        return contract

    @classmethod
    async def get_contract(cls, db: AsyncSession, contract_id: str) -> Contract:
        stmt = select(Contract).where(
            and_(Contract.id == contract_id, Contract.is_deleted == False)
        ).options(selectinload(Contract.documents), selectinload(Contract.performances))
        res = await db.execute(stmt)
        contract = res.scalars().first()
        if not contract:
            raise EntityNotFoundError("Contract", contract_id)
        return contract

    @classmethod
    async def list_contracts(
        cls,
        db: AsyncSession,
        mine_id: Optional[str] = None,
        contractor_id: Optional[str] = None,
        status: Optional[str] = None,
        contract_type: Optional[str] = None
    ) -> List[Contract]:
        stmt = select(Contract).where(Contract.is_deleted == False).options(
            selectinload(Contract.documents), selectinload(Contract.performances)
        )

        if mine_id:
            stmt = stmt.where(Contract.mine_id == mine_id)
        if contractor_id:
            stmt = stmt.where(Contract.contractor_id == contractor_id)
        if status:
            stmt = stmt.where(Contract.status == status)
        if contract_type:
            stmt = stmt.where(Contract.contract_type == contract_type)

        stmt = stmt.order_by(Contract.end_date.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # ------------------ DOCUMENT MANAGEMENT ------------------

    @classmethod
    async def store_document_metadata(
        cls,
        db: AsyncSession,
        contractor_id: str,
        document_type: str,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        mime_type: str,
        contract_id: Optional[str] = None,
        valid_from: Optional[date] = None,
        valid_until: Optional[date] = None,
        user_id: Optional[str] = None
    ) -> ContractDocument:
        contractor = await cls.get_contractor(db, contractor_id)

        doc = ContractDocument(
            id=generate_uuid(),
            contractor_id=contractor.id,
            contract_id=contract_id,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            uploaded_by_user_id=user_id,
            valid_from=valid_from,
            valid_until=valid_until
        )
        db.add(doc)
        await db.flush()

        await audit_service.log_action(
            db=db,
            action="CONTRACTOR_DOCUMENT_UPLOADED",
            entity_type="ContractDocument",
            entity_id=doc.id,
            changes={"document_type": document_type, "file_name": file_name},
            user_id=user_id,
            mine_id=contractor.mine_id
        )
        await db.commit()
        await db.refresh(doc)
        return doc

    # ------------------ COMPLIANCE TRACKING ------------------

    @classmethod
    async def record_compliance_check(
        cls,
        db: AsyncSession,
        contractor_id: str,
        payload: ContractComplianceCreate,
        user_id: Optional[str] = None
    ) -> ContractCompliance:
        contractor = await cls.get_contractor(db, contractor_id)

        comp = ContractCompliance(
            id=generate_uuid(),
            contractor_id=contractor.id,
            compliance_item=payload.compliance_item,
            category=payload.category,
            status=payload.status,
            score_deduction=payload.score_deduction,
            remarks=payload.remarks,
            inspected_at=utc_now()
        )
        db.add(comp)
        await db.flush()

        # Recalculate contractor compliance score
        await cls._recalculate_compliance_score(db, contractor)

        # Trigger alert if non-compliant
        if payload.status == "NON_COMPLIANT":
            alert = Alert(
                id=generate_uuid(),
                mine_id=contractor.mine_id,
                zone_id="",  # Mine wide
                title=f"Contractor Non-Compliance Flagged: {contractor.company_name}",
                message=f"Statutory/Safety violation logged: '{payload.compliance_item}' ({payload.category}). Remarks: {payload.remarks or 'N/A'}",
                alert_type="COMPLIANCE_BREACH",
                severity="HIGH",
                channel="IN_APP",
                target_role="MINE_MANAGER",
                status="PENDING"
            )
            db.add(alert)

        await db.commit()
        await db.refresh(comp)
        return comp

    @classmethod
    async def _recalculate_compliance_score(cls, db: AsyncSession, contractor: Contractor):
        stmt = select(ContractCompliance).where(
            and_(
                ContractCompliance.contractor_id == contractor.id,
                ContractCompliance.is_deleted == False
            )
        )
        res = await db.execute(stmt)
        checks = list(res.scalars().all())

        total_deduction = sum(c.score_deduction for c in checks if c.status == "NON_COMPLIANT")
        new_score = max(0.0, round(100.0 - total_deduction, 2))
        contractor.compliance_score = new_score

        if new_score >= 85.0:
            contractor.compliance_status = "COMPLIANT"
        elif new_score >= 60.0:
            contractor.compliance_status = "WARNING"
        else:
            contractor.compliance_status = "NON_COMPLIANT"

        contractor.updated_at = utc_now()

    # ------------------ PERFORMANCE TRACKING ------------------

    @classmethod
    async def record_performance_evaluation(
        cls,
        db: AsyncSession,
        contractor_id: str,
        payload: ContractPerformanceCreate,
        user_id: Optional[str] = None
    ) -> ContractPerformance:
        contractor = await cls.get_contractor(db, contractor_id)

        perf = ContractPerformance(
            id=generate_uuid(),
            contractor_id=contractor.id,
            contract_id=payload.contract_id,
            rating=payload.rating,
            period=payload.period,
            evaluated_by=payload.evaluated_by,
            sla_adherence_percent=payload.sla_adherence_percent,
            safety_incident_count=payload.safety_incident_count,
            remarks=payload.remarks
        )
        db.add(perf)
        await db.flush()

        # Recalculate dynamic overall performance score
        stmt = select(func.avg(ContractPerformance.rating)).where(
            and_(
                ContractPerformance.contractor_id == contractor.id,
                ContractPerformance.is_deleted == False
            )
        )
        res = await db.execute(stmt)
        avg_rating = res.scalar()
        if avg_rating is not None:
            contractor.performance_score = round(float(avg_rating), 2)
            contractor.updated_at = utc_now()

        await db.commit()
        await db.refresh(perf)
        return perf

    # ------------------ CONTRACT RENEWAL & EXPIRY TRACKING ------------------

    @classmethod
    async def renew_contract(
        cls,
        db: AsyncSession,
        contract_id: str,
        payload: ContractRenewalRequest,
        user_id: Optional[str] = None
    ) -> Contract:
        contract = await cls.get_contract(db, contract_id)

        if contract.end_date >= payload.new_end_date:
            raise InvalidStateTransitionError("Contract", str(contract.end_date), str(payload.new_end_date))

        old_end_date = contract.end_date
        contract.end_date = payload.new_end_date
        if payload.revised_value and payload.revised_value > 0:
            contract.contract_value = payload.revised_value
        contract.status = "RENEWED"
        contract.renewal_count += 1
        contract.updated_at = utc_now()

        await audit_service.log_action(
            db=db,
            action="CONTRACT_RENEWED",
            entity_type="Contract",
            entity_id=contract.id,
            changes={
                "previous_end_date": str(old_end_date),
                "new_end_date": str(payload.new_end_date),
                "renewal_count": contract.renewal_count,
                "remarks": payload.remarks
            },
            user_id=user_id,
            mine_id=contract.mine_id
        )
        await db.commit()
        await db.refresh(contract)
        return contract

    @classmethod
    async def get_expiring_contracts(
        cls, db: AsyncSession, mine_id: Optional[str] = None, days: int = 30
    ) -> List[Contract]:
        today = date.today()
        target_date = today + timedelta(days=days)

        stmt = select(Contract).where(
            and_(
                Contract.is_deleted == False,
                Contract.status.in_(["ACTIVE", "EXPIRING_SOON"]),
                Contract.end_date >= today,
                Contract.end_date <= target_date
            )
        ).options(selectinload(Contract.documents), selectinload(Contract.performances)).order_by(Contract.end_date.asc())

        if mine_id:
            stmt = stmt.where(Contract.mine_id == mine_id)

        res = await db.execute(stmt)
        contracts = list(res.scalars().all())

        # Auto-update status to EXPIRING_SOON and trigger alerts if within threshold
        for c in contracts:
            if c.status != "EXPIRING_SOON":
                c.status = "EXPIRING_SOON"
                # Trigger alert
                days_left = (c.end_date - today).days
                alert = Alert(
                    id=generate_uuid(),
                    mine_id=c.mine_id,
                    zone_id="",
                    title=f"Contract Expiry Warning: {c.contract_number}",
                    message=f"Contract '{c.title}' is expiring in {days_left} days (End Date: {c.end_date}). Action required for renewal.",
                    alert_type="EXPIRY_WARNING",
                    severity="HIGH" if days_left <= 7 else "MEDIUM",
                    channel="IN_APP",
                    target_role="MINE_MANAGER",
                    status="PENDING"
                )
                db.add(alert)

        await db.commit()
        return contracts

    @classmethod
    async def get_dashboard_stats(cls, db: AsyncSession, mine_id: Optional[str] = None) -> ContractorDashboardStats:
        contractors = await cls.list_contractors(db, mine_id=mine_id)
        contracts = await cls.list_contracts(db, mine_id=mine_id)

        total_contractors = len(contractors)
        active_contractors = sum(1 for c in contractors if c.status == "ACTIVE")
        suspended_contractors = sum(1 for c in contractors if c.status == "SUSPENDED")

        active_contracts = [c for c in contracts if c.status in ["ACTIVE", "EXPIRING_SOON", "RENEWED"]]
        total_active_contracts = len(active_contracts)
        total_contract_value = sum(c.contract_value for c in active_contracts)

        today = date.today()
        expiring_contracts_count = sum(
            1 for c in contracts if c.end_date >= today and c.end_date <= today + timedelta(days=30)
        )

        avg_comp = sum(c.compliance_score for c in contractors) / total_contractors if total_contractors > 0 else 100.0
        non_compliant_count = sum(1 for c in contractors if c.compliance_status == "NON_COMPLIANT")
        avg_perf = sum(c.performance_score for c in contractors) / total_contractors if total_contractors > 0 else 5.0

        return ContractorDashboardStats(
            total_contractors=total_contractors,
            active_contractors=active_contractors,
            suspended_contractors=suspended_contractors,
            total_active_contracts=total_active_contracts,
            total_contract_value=round(total_contract_value, 2),
            expiring_contracts_count=expiring_contracts_count,
            average_compliance_score=round(avg_comp, 2),
            non_compliant_contractors_count=non_compliant_count,
            average_performance_rating=round(avg_perf, 2)
        )


contractor_service = ContractorService()

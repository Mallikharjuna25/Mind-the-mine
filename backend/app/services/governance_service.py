from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from fastapi import HTTPException, status

from app.models.governance_models import (
    Grievance, GrievanceEvidence, GrievanceResolution, 
    ApprovalRequest, ApprovalHistory
)
from app.schemas.governance_schemas import (
    GrievanceCreate, GrievanceUpdate, GrievanceResolutionCreate,
    ApprovalRequestCreate, ApprovalAction, DashboardStats
)
from app.services.audit_service import audit_service
from app.models.workflow_models import Alert, Escalation
from app.models.audit_models import AuditLog

class GovernanceService:
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession, mine_id: str) -> DashboardStats:
        # Get grievance stats
        stmt = select(func.count(Grievance.id)).where(Grievance.mine_id == mine_id, Grievance.is_deleted == False)
        total_grievances = (await db.execute(stmt)).scalar() or 0
        
        stmt = select(func.count(Grievance.id)).where(Grievance.mine_id == mine_id, Grievance.status == "OPEN", Grievance.is_deleted == False)
        open_grievances = (await db.execute(stmt)).scalar() or 0
        
        stmt = select(func.count(Grievance.id)).where(Grievance.mine_id == mine_id, Grievance.status == "RESOLVED", Grievance.is_deleted == False)
        resolved_grievances = (await db.execute(stmt)).scalar() or 0
        
        stmt = select(func.count(Grievance.id)).where(Grievance.mine_id == mine_id, Grievance.is_escalated == True, Grievance.is_deleted == False)
        escalated_grievances = (await db.execute(stmt)).scalar() or 0
        
        # Get approval stats
        stmt = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.mine_id == mine_id, ApprovalRequest.status == "PENDING", ApprovalRequest.is_deleted == False)
        pending_approvals = (await db.execute(stmt)).scalar() or 0
        
        stmt = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.mine_id == mine_id, ApprovalRequest.is_deleted == False)
        total_approvals = (await db.execute(stmt)).scalar() or 0
        
        stmt = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.mine_id == mine_id, ApprovalRequest.status == "APPROVED", ApprovalRequest.is_deleted == False)
        approved = (await db.execute(stmt)).scalar() or 0
        
        approval_rate = (approved / total_approvals * 100) if total_approvals > 0 else 0.0
        
        return DashboardStats(
            total_grievances=total_grievances,
            open_grievances=open_grievances,
            resolved_grievances=resolved_grievances,
            escalated_grievances=escalated_grievances,
            pending_approvals=pending_approvals,
            approval_rate_percentage=round(approval_rate, 2)
        )

    @staticmethod
    async def create_grievance(db: AsyncSession, obj_in: GrievanceCreate, user_id: str) -> Grievance:
        now = datetime.now(timezone.utc)
        from datetime import timedelta
        
        sla_hours = {"LOW": 72, "MEDIUM": 48, "HIGH": 24, "CRITICAL": 12}.get(obj_in.priority.upper(), 48)
        sla_deadline = now + timedelta(hours=sla_hours)
        
        db_obj = Grievance(
            **obj_in.model_dump(),
            sla_deadline=sla_deadline
        )
        db.add(db_obj)
        await db.flush()
        
        await audit_service.log_action(
            db=db, action="CREATE_GRIEVANCE", entity_type="GRIEVANCE",
            entity_id=db_obj.id, changes=obj_in.model_dump(),
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_grievances(
        db: AsyncSession, mine_id: str, category: Optional[str] = None, 
        priority: Optional[str] = None, status: Optional[str] = None,
        skip: int = 0, limit: int = 100
    ) -> List[Grievance]:
        stmt = select(Grievance).where(Grievance.mine_id == mine_id, Grievance.is_deleted == False)
        if category:
            stmt = stmt.where(Grievance.category == category)
        if priority:
            stmt = stmt.where(Grievance.priority == priority)
        if status:
            stmt = stmt.where(Grievance.status == status)
        stmt = stmt.offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_grievance_by_id(db: AsyncSession, grievance_id: str) -> Grievance:
        from sqlalchemy.orm import selectinload
        stmt = select(Grievance).options(
            selectinload(Grievance.evidences),
            selectinload(Grievance.resolutions)
        ).where(Grievance.id == grievance_id, Grievance.is_deleted == False)
        res = await db.execute(stmt)
        db_obj = res.scalars().first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Grievance not found")
        return db_obj

    @staticmethod
    async def update_grievance(db: AsyncSession, grievance_id: str, obj_in: GrievanceUpdate, user_id: str) -> Grievance:
        db_obj = await GovernanceService.get_grievance_by_id(db, grievance_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await audit_service.log_action(
            db=db, action="UPDATE_GRIEVANCE", entity_type="GRIEVANCE",
            entity_id=db_obj.id, changes=update_data,
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def resolve_grievance(db: AsyncSession, grievance_id: str, obj_in: GrievanceResolutionCreate, user_id: str) -> Grievance:
        db_obj = await GovernanceService.get_grievance_by_id(db, grievance_id)
        if db_obj.status == "RESOLVED" or db_obj.status == "CLOSED":
            raise HTTPException(status_code=400, detail="Grievance is already resolved or closed")
            
        resolution = GrievanceResolution(
            grievance_id=db_obj.id,
            resolution_action=obj_in.resolution_action,
            resolution_notes=obj_in.resolution_notes,
            resolved_by_user_id=user_id,
            resolved_at=datetime.now(timezone.utc)
        )
        db.add(resolution)
        db_obj.status = "RESOLVED"
        
        await audit_service.log_action(
            db=db, action="RESOLVE_GRIEVANCE", entity_type="GRIEVANCE",
            entity_id=db_obj.id, changes={"status": "RESOLVED", "action": obj_in.resolution_action},
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def close_grievance(db: AsyncSession, grievance_id: str, user_id: str) -> Grievance:
        db_obj = await GovernanceService.get_grievance_by_id(db, grievance_id)
        if db_obj.status == "CLOSED":
            raise HTTPException(status_code=400, detail="Grievance is already closed")
            
        db_obj.status = "CLOSED"
        await audit_service.log_action(
            db=db, action="CLOSE_GRIEVANCE", entity_type="GRIEVANCE",
            entity_id=db_obj.id, changes={"status": "CLOSED"},
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def create_approval_request(db: AsyncSession, obj_in: ApprovalRequestCreate, user_id: str) -> ApprovalRequest:
        db_obj = ApprovalRequest(**obj_in.model_dump())
        if not db_obj.requester_id:
            db_obj.requester_id = user_id
            
        db.add(db_obj)
        await db.flush()
        
        history = ApprovalHistory(
            approval_request_id=db_obj.id,
            actor_user_id=user_id,
            action="SUBMITTED",
            previous_status="NONE",
            new_status="PENDING",
            remarks=obj_in.remarks,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(history)
        
        await audit_service.log_action(
            db=db, action="CREATE_APPROVAL_REQUEST", entity_type="APPROVAL",
            entity_id=db_obj.id, changes=obj_in.model_dump(),
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_approval_requests(
        db: AsyncSession, mine_id: str, approval_type: Optional[str] = None, 
        status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[ApprovalRequest]:
        stmt = select(ApprovalRequest).where(ApprovalRequest.mine_id == mine_id, ApprovalRequest.is_deleted == False)
        if approval_type:
            stmt = stmt.where(ApprovalRequest.approval_type == approval_type)
        if status:
            stmt = stmt.where(ApprovalRequest.status == status)
        stmt = stmt.offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_approval_request_by_id(db: AsyncSession, request_id: str) -> ApprovalRequest:
        from sqlalchemy.orm import selectinload
        stmt = select(ApprovalRequest).options(selectinload(ApprovalRequest.histories)).where(ApprovalRequest.id == request_id, ApprovalRequest.is_deleted == False)
        res = await db.execute(stmt)
        db_obj = res.scalars().first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Approval request not found")
        return db_obj

    @staticmethod
    async def action_approval_request(db: AsyncSession, request_id: str, obj_in: ApprovalAction, user_id: str) -> ApprovalRequest:
        db_obj = await GovernanceService.get_approval_request_by_id(db, request_id)
        if db_obj.status in ["APPROVED", "REJECTED", "CANCELLED"]:
            raise HTTPException(status_code=400, detail=f"Cannot action on a request in {db_obj.status} status")
            
        action_map = {
            "APPROVE": "APPROVED",
            "REJECT": "REJECTED",
            "UNDER_REVIEW": "UNDER_REVIEW"
        }
        if obj_in.action not in action_map:
            raise HTTPException(status_code=400, detail="Invalid action")
            
        prev_status = db_obj.status
        new_status = action_map[obj_in.action]
        db_obj.status = new_status
        
        history = ApprovalHistory(
            approval_request_id=db_obj.id,
            actor_user_id=user_id,
            action=obj_in.action,
            previous_status=prev_status,
            new_status=new_status,
            remarks=obj_in.remarks,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(history)
        
        await audit_service.log_action(
            db=db, action=f"{obj_in.action}_APPROVAL", entity_type="APPROVAL",
            entity_id=db_obj.id, changes={"previous_status": prev_status, "new_status": new_status, "remarks": obj_in.remarks},
            user_id=user_id, mine_id=db_obj.mine_id
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def evaluate_escalations(db: AsyncSession, mine_id: str) -> dict:
        now = datetime.now(timezone.utc)
        stmt = select(Grievance).where(
            Grievance.mine_id == mine_id, 
            Grievance.status.in_(["OPEN", "ASSIGNED", "UNDER_REVIEW"]),
            Grievance.is_escalated == False,
            Grievance.sla_deadline < now,
            Grievance.is_deleted == False
        )
        res = await db.execute(stmt)
        breached_grievances = res.scalars().all()
        
        escalated_count = 0
        for g in breached_grievances:
            g.is_escalated = True
            
            # Create Escalation record
            escalation = Escalation(
                mine_id=mine_id,
                entity_type="GRIEVANCE",
                entity_id=g.id,
                escalation_level=2,
                reason="SLA Deadline Breached",
                status="ACTIVE"
            )
            db.add(escalation)
            
            # Create Alert
            alert = Alert(
                mine_id=mine_id,
                alert_type="ESCALATION",
                severity="HIGH",
                title=f"Grievance Escalated: {g.title}",
                message=f"Grievance {g.id} has breached SLA and requires immediate attention.",
                entity_type="GRIEVANCE",
                entity_id=g.id
            )
            db.add(alert)
            escalated_count += 1
            
        await db.commit()
        return {"escalated_count": escalated_count, "message": "Escalation evaluation completed."}

    @staticmethod
    async def query_audit_trail(
        db: AsyncSession, mine_id: str, action: Optional[str] = None, 
        entity_type: Optional[str] = None, user_id: Optional[str] = None,
        skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.mine_id == mine_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if user_id:
            stmt = stmt.where(AuditLog.user_id == user_id)
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

governance_service = GovernanceService()

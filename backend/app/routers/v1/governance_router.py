from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user_with_permissions
from app.models.user_models import User
from app.schemas.common_schemas import ApiResponse
from app.schemas.governance_schemas import (
    GrievanceCreate, GrievanceUpdate, GrievanceResolutionCreate, GrievanceResponse,
    ApprovalRequestCreate, ApprovalAction, ApprovalRequestResponse, DashboardStats
)
from app.services.governance_service import governance_service

router = APIRouter(prefix="/mine/governance", tags=["Governance & Approval Workflow"])

# Dashboard & Reports
@router.get("/dashboard", response_model=ApiResponse[DashboardStats])
async def get_dashboard(
    mine_id: str = Query(..., description="Mine ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.report"]))
):
    stats = await governance_service.get_dashboard_stats(db, mine_id)
    return ApiResponse(data=stats)

# Grievance Management
@router.post("/grievances", response_model=ApiResponse[GrievanceResponse])
async def create_grievance(
    grievance: GrievanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.create"]))
):
    db_obj = await governance_service.create_grievance(db, grievance, current_user.id)
    return ApiResponse(data=db_obj)

@router.get("/grievances", response_model=ApiResponse[List[GrievanceResponse]])
async def get_grievances(
    mine_id: str = Query(..., description="Mine ID"),
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.read"]))
):
    db_objs = await governance_service.get_grievances(db, mine_id, category, priority, status, skip, limit)
    return ApiResponse(data=db_objs)

@router.get("/grievances/{id}", response_model=ApiResponse[GrievanceResponse])
async def get_grievance(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.read"]))
):
    db_obj = await governance_service.get_grievance_by_id(db, id)
    return ApiResponse(data=db_obj)

@router.put("/grievances/{id}", response_model=ApiResponse[GrievanceResponse])
async def update_grievance(
    id: str,
    update_data: GrievanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.update"]))
):
    db_obj = await governance_service.update_grievance(db, id, update_data, current_user.id)
    return ApiResponse(data=db_obj)

@router.post("/grievances/{id}/resolve", response_model=ApiResponse[GrievanceResponse])
async def resolve_grievance(
    id: str,
    resolution: GrievanceResolutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.resolve"]))
):
    db_obj = await governance_service.resolve_grievance(db, id, resolution, current_user.id)
    return ApiResponse(data=db_obj)

@router.post("/grievances/{id}/close", response_model=ApiResponse[GrievanceResponse])
async def close_grievance(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.grievance.resolve"]))
):
    db_obj = await governance_service.close_grievance(db, id, current_user.id)
    return ApiResponse(data=db_obj)

# Approval Workflow
@router.post("/approvals", response_model=ApiResponse[ApprovalRequestResponse])
async def create_approval_request(
    request: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.approval.create"]))
):
    db_obj = await governance_service.create_approval_request(db, request, current_user.id)
    return ApiResponse(data=db_obj)

@router.get("/approvals", response_model=ApiResponse[List[ApprovalRequestResponse]])
async def get_approval_requests(
    mine_id: str = Query(..., description="Mine ID"),
    approval_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.approval.read"]))
):
    db_objs = await governance_service.get_approval_requests(db, mine_id, approval_type, status, skip, limit)
    return ApiResponse(data=db_objs)

@router.get("/approvals/{id}", response_model=ApiResponse[ApprovalRequestResponse])
async def get_approval_request(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.approval.read"]))
):
    db_obj = await governance_service.get_approval_request_by_id(db, id)
    return ApiResponse(data=db_obj)

@router.post("/approvals/{id}/action", response_model=ApiResponse[ApprovalRequestResponse])
async def action_approval_request(
    id: str,
    action_data: ApprovalAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.approval.execute"]))
):
    db_obj = await governance_service.action_approval_request(db, id, action_data, current_user.id)
    return ApiResponse(data=db_obj)

# Escalation Engine
@router.post("/escalations/evaluate", response_model=ApiResponse[dict])
async def evaluate_escalations(
    mine_id: str = Query(..., description="Mine ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.escalation.execute"]))
):
    result = await governance_service.evaluate_escalations(db, mine_id)
    return ApiResponse(data=result)


@router.post("/evaluate-expiries", response_model=ApiResponse[dict])
async def evaluate_workforce_expiries(
    mine_id: Optional[str] = Query(None, description="Mine ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.report"]))
):
    from app.services.workforce_governance_jobs import workforce_jobs
    res = await workforce_jobs.evaluate_all_expiries_and_slas(db, mine_id=mine_id)
    return ApiResponse(message="Workforce statutory expiry and SLA evaluation completed", data=res)

# Audit Trail
@router.get("/audit-trail", response_model=ApiResponse[list])
async def get_audit_trail(
    mine_id: str = Query(..., description="Mine ID"),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permissions(["governance.audit.read"]))
):
    db_objs = await governance_service.query_audit_trail(db, mine_id, action, entity_type, user_id, skip, limit)
    serialized = [
        {
            "id": obj.id,
            "mine_id": obj.mine_id,
            "user_id": obj.user_id,
            "user_email": obj.user_email,
            "action": obj.action,
            "entity_type": obj.entity_type,
            "entity_id": obj.entity_id,
            "changes": obj.changes_json,
            "previous_hash": obj.previous_hash,
            "current_hash": obj.block_hash,
            "block_hash": obj.block_hash,
            "created_at": obj.created_at.isoformat() if obj.created_at else None
        }
        for obj in db_objs
    ]
    return ApiResponse(data=serialized)

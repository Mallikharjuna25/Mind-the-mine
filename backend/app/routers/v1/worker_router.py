"""
Worker & Compliance Management API Router (Module 3 -> Task 2)
Exposes RESTful endpoints for Worker Registry, Attendance, Training, Certifications, PPE, Authorization & Reports.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenPayload, require_permission
from app.schemas.worker_schemas import (
    WorkerCreate, WorkerUpdate, WorkerResponse,
    WorkerAttendanceCreate, WorkerAttendanceResponse,
    WorkerTrainingCreate, WorkerTrainingResponse,
    WorkerCertificationCreate, WorkerCertificationResponse,
    WorkerPPECreate, WorkerPPEResponse,
    WorkerAuthorizationCreate, WorkerAuthorizationResponse,
    WorkerDashboardStats, WorkerReportsSummary
)
from app.schemas.common_schemas import ApiResponse
from app.services.worker_service import worker_service

router = APIRouter(prefix="/mine", tags=["Worker & Compliance Management (Module 3)"])


@router.get("/workers/dashboard", response_model=ApiResponse[WorkerDashboardStats])
async def get_worker_dashboard_stats(
    mine_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stats = await worker_service.get_dashboard_stats(db=db, mine_id=mine_id)
    return ApiResponse(message="Worker dashboard statistics", data=stats)


@router.get("/workers/reports/summary", response_model=ApiResponse[WorkerReportsSummary])
async def get_worker_reports_summary(
    mine_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    summary = await worker_service.get_reports_summary(db=db, mine_id=mine_id)
    return ApiResponse(message="Worker workforce & compliance reports summary", data=summary)


@router.post("/workers", response_model=ApiResponse[WorkerResponse])
async def create_worker(
    payload: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.create"))
):
    worker = await worker_service.create_worker(db=db, payload=payload, user_id=current_user.sub)
    return ApiResponse(message="Worker registered successfully", data=WorkerResponse.model_validate(worker))


@router.get("/workers", response_model=ApiResponse[List[WorkerResponse]])
async def list_workers(
    mine_id: Optional[str] = Query(None),
    contractor_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    workers = await worker_service.list_workers(
        db=db, mine_id=mine_id, contractor_id=contractor_id,
        department=department, status=status, search=search
    )
    return ApiResponse(data=[WorkerResponse.model_validate(w) for w in workers])


@router.get("/workers/{worker_id}", response_model=ApiResponse[WorkerResponse])
async def get_worker_profile(
    worker_id: str,
    db: AsyncSession = Depends(get_db)
):
    worker = await worker_service.get_worker(db=db, worker_id=worker_id)
    return ApiResponse(data=WorkerResponse.model_validate(worker))


@router.put("/workers/{worker_id}", response_model=ApiResponse[WorkerResponse])
async def update_worker(
    worker_id: str,
    payload: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.update"))
):
    worker = await worker_service.update_worker(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Worker profile updated successfully", data=WorkerResponse.model_validate(worker))


@router.delete("/workers/{worker_id}", response_model=ApiResponse[dict])
async def delete_worker(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.delete"))
):
    await worker_service.delete_worker(db=db, worker_id=worker_id, user_id=current_user.sub)
    return ApiResponse(message="Worker record soft-deleted successfully", data={"id": worker_id})


# ------------------ ATTENDANCE ENDPOINTS ------------------

@router.post("/workers/{worker_id}/attendance", response_model=ApiResponse[WorkerAttendanceResponse])
async def mark_attendance(
    worker_id: str,
    payload: WorkerAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.attendance"))
):
    att = await worker_service.mark_attendance(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Worker attendance recorded", data=WorkerAttendanceResponse.model_validate(att))


@router.get("/workers/attendance", response_model=ApiResponse[List[WorkerAttendanceResponse]])
async def list_attendances(
    mine_id: Optional[str] = Query(None),
    worker_id: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    atts = await worker_service.list_attendances(db=db, mine_id=mine_id, worker_id=worker_id, shift=shift)
    return ApiResponse(data=[WorkerAttendanceResponse.model_validate(a) for a in atts])


# ------------------ TRAINING ENDPOINTS ------------------

@router.post("/workers/{worker_id}/trainings", response_model=ApiResponse[WorkerTrainingResponse])
async def assign_training(
    worker_id: str,
    payload: WorkerTrainingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.training"))
):
    tr = await worker_service.assign_training(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Training program assigned", data=WorkerTrainingResponse.model_validate(tr))


@router.get("/workers/trainings", response_model=ApiResponse[List[WorkerTrainingResponse]])
async def list_trainings(
    worker_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    trs = await worker_service.list_trainings(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerTrainingResponse.model_validate(t) for t in trs])


# ------------------ CERTIFICATION ENDPOINTS ------------------

@router.post("/workers/{worker_id}/certifications", response_model=ApiResponse[WorkerCertificationResponse])
async def register_certification(
    worker_id: str,
    payload: WorkerCertificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.certification"))
):
    cert = await worker_service.register_certification(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Worker certification registered", data=WorkerCertificationResponse.model_validate(cert))


@router.get("/workers/certifications", response_model=ApiResponse[List[WorkerCertificationResponse]])
async def list_certifications(
    worker_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    certs = await worker_service.list_certifications(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerCertificationResponse.model_validate(c) for c in certs])


# ------------------ PPE ENDPOINTS ------------------

@router.post("/workers/{worker_id}/ppe", response_model=ApiResponse[WorkerPPEResponse])
async def assign_ppe(
    worker_id: str,
    payload: WorkerPPECreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.ppe"))
):
    ppe = await worker_service.assign_ppe(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="PPE eligibility & issuance assigned", data=WorkerPPEResponse.model_validate(ppe))


@router.get("/workers/ppe", response_model=ApiResponse[List[WorkerPPEResponse]])
async def list_ppes(
    worker_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    ppes = await worker_service.list_ppes(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerPPEResponse.model_validate(p) for p in ppes])


# ------------------ AUTHORIZATION ENDPOINTS ------------------

@router.post("/workers/{worker_id}/authorizations", response_model=ApiResponse[WorkerAuthorizationResponse])
async def grant_authorization(
    worker_id: str,
    payload: WorkerAuthorizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.authorize"))
):
    auth = await worker_service.grant_authorization(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Work authorization permit granted", data=WorkerAuthorizationResponse.model_validate(auth))


@router.post("/workers/authorizations/{auth_id}/revoke", response_model=ApiResponse[WorkerAuthorizationResponse])
async def revoke_authorization(
    auth_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.authorize"))
):
    auth = await worker_service.revoke_authorization(db=db, authorization_id=auth_id, user_id=current_user.sub)
    return ApiResponse(message="Work authorization permit revoked", data=WorkerAuthorizationResponse.model_validate(auth))


@router.get("/workers/authorizations", response_model=ApiResponse[List[WorkerAuthorizationResponse]])
async def list_authorizations(
    worker_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    auths = await worker_service.list_authorizations(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerAuthorizationResponse.model_validate(a) for a in auths])

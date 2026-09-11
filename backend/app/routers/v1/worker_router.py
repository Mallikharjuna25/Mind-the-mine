"""
Worker & Compliance Management API Router (Module 3 -> Task 2)
Exposes RESTful endpoints for Worker Registry, Attendance, Training, Certifications, PPE, Authorization & Reports.
"""

import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import TokenPayload, require_permission, get_current_user
from app.schemas.worker_schemas import (
    WorkerCreate, WorkerUpdate, WorkerResponse,
    WorkerAttendanceCreate, WorkerAttendanceResponse,
    WorkerTrainingCreate, WorkerTrainingResponse,
    WorkerCertificationCreate, WorkerCertificationResponse,
    WorkerPPECreate, WorkerPPEResponse,
    WorkerAuthorizationCreate, WorkerAuthorizationResponse,
    WorkerInsuranceCreate, WorkerInsuranceResponse,
    WorkerLeaveCreate, WorkerLeaveResponse, WorkerLeaveAction,
    WorkerPassCreate, WorkerPassAction, WorkerPassResponse,
    WorkerDocumentResponse, WorkerDocumentReviewAction,
    WorkerInductionCreate, WorkerInductionResponse, WorkerInductionStats,
    WorkerZoneClearanceResponse,
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


# ------------------ WORKER SELF PROFILE ENDPOINT ------------------

@router.get("/workers/me/profile", response_model=ApiResponse[WorkerResponse])
async def get_my_worker_profile(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    # Try finding worker by user email
    worker = await worker_service.get_worker_by_email(db, email=current_user.email)
    if not worker:
        # Fallback to the first active worker in the mine so any user previewing the portal sees a rich profile
        workers = await worker_service.list_workers(db=db, status="ACTIVE")
        if workers:
            worker = await worker_service.get_worker(db, workers[0].id)
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker profile not found.")

    return ApiResponse(message="Worker profile retrieved", data=WorkerResponse.model_validate(worker))


# ------------------ INSURANCE ENDPOINTS ------------------

@router.post("/workers/{worker_id}/insurances", response_model=ApiResponse[WorkerInsuranceResponse])
async def create_worker_insurance(
    worker_id: str,
    payload: WorkerInsuranceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    ins = await worker_service.create_insurance(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Worker insurance policy registered", data=WorkerInsuranceResponse.model_validate(ins))


@router.get("/workers/{worker_id}/insurances", response_model=ApiResponse[List[WorkerInsuranceResponse]])
async def list_worker_insurances(
    worker_id: str,
    db: AsyncSession = Depends(get_db)
):
    ins_list = await worker_service.list_insurances(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerInsuranceResponse.model_validate(i) for i in ins_list])


@router.get("/workers/insurances", response_model=ApiResponse[List[WorkerInsuranceResponse]])
async def list_all_insurances(
    worker_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    ins_list = await worker_service.list_insurances(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerInsuranceResponse.model_validate(i) for i in ins_list])


# ------------------ LEAVE & PERMISSION ENDPOINTS ------------------

@router.post("/workers/{worker_id}/leaves", response_model=ApiResponse[WorkerLeaveResponse])
async def apply_worker_leave(
    worker_id: str,
    payload: WorkerLeaveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    leave = await worker_service.apply_leave(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Leave application submitted successfully", data=WorkerLeaveResponse.model_validate(leave))


@router.get("/workers/{worker_id}/leaves", response_model=ApiResponse[List[WorkerLeaveResponse]])
async def list_worker_leaves(
    worker_id: str,
    db: AsyncSession = Depends(get_db)
):
    leaves = await worker_service.list_leaves(db=db, worker_id=worker_id)
    return ApiResponse(data=[WorkerLeaveResponse.model_validate(l) for l in leaves])


@router.get("/workers/leaves", response_model=ApiResponse[List[WorkerLeaveResponse]])
async def list_all_leaves(
    worker_id: Optional[str] = Query(None),
    mine_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    leaves = await worker_service.list_leaves(db=db, worker_id=worker_id, mine_id=mine_id)
    return ApiResponse(data=[WorkerLeaveResponse.model_validate(l) for l in leaves])


@router.put("/workers/leaves/{leave_id}/action", response_model=ApiResponse[WorkerLeaveResponse])
async def action_worker_leave(
    leave_id: str,
    payload: WorkerLeaveAction,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    approver = current_user.email
    leave = await worker_service.action_leave(
        db=db, leave_id=leave_id, payload=payload, approver_name=approver
    )
    return ApiResponse(message=f"Leave status updated to {payload.status}", data=WorkerLeaveResponse.model_validate(leave))


# ------------------ RFID PASS ENDPOINTS ------------------

@router.post("/workers/{worker_id}/passes", response_model=ApiResponse[WorkerPassResponse])
async def issue_worker_pass(
    worker_id: str,
    payload: WorkerPassCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.update"))
):
    pass_obj = await worker_service.register_pass(
        db=db, worker_id=worker_id, payload=payload, issued_by=current_user.email or current_user.sub
    )
    return ApiResponse(message="RFID Pass registered and activated successfully", data=WorkerPassResponse.model_validate(pass_obj))


@router.put("/workers/passes/{pass_id}/action", response_model=ApiResponse[WorkerPassResponse])
async def action_worker_pass(
    pass_id: str,
    payload: WorkerPassAction,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.update"))
):
    actor = current_user.email or current_user.sub
    pass_obj = await worker_service.action_pass(db=db, pass_id=pass_id, payload=payload, actor=actor)
    return ApiResponse(message=f"Pass status updated to {pass_obj.status}", data=WorkerPassResponse.model_validate(pass_obj))


@router.get("/workers/passes", response_model=ApiResponse[List[WorkerPassResponse]])
async def list_worker_passes(
    worker_id: Optional[str] = Query(None),
    mine_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    passes = await worker_service.list_passes(db=db, worker_id=worker_id, mine_id=mine_id, status=status)
    return ApiResponse(data=[WorkerPassResponse.model_validate(p) for p in passes])


# ------------------ WORKER DOCUMENTS & OCR ENDPOINTS ------------------

@router.post("/workers/{worker_id}/documents", response_model=ApiResponse[WorkerDocumentResponse])
async def upload_worker_document(
    worker_id: str,
    document_type: str = Form(default="IDENTITY_CARD"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.document.upload"))
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"worker_{worker_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    doc = await worker_service.upload_worker_document(
        db=db,
        worker_id=worker_id,
        contractor_id=None,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/pdf",
        user_id=current_user.email or current_user.sub
    )
    return ApiResponse(
        message=f"Document uploaded and processed via OCR (Status: {doc.ocr_status}, Confidence: {doc.ocr_confidence:.2f})",
        data=WorkerDocumentResponse.model_validate(doc)
    )


@router.put("/workers/documents/{doc_id}/review", response_model=ApiResponse[WorkerDocumentResponse])
async def review_worker_document(
    doc_id: str,
    payload: WorkerDocumentReviewAction,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.document.review"))
):
    reviewer = current_user.email or current_user.sub
    doc = await worker_service.review_worker_document(
        db=db, document_id=doc_id, payload=payload, reviewer=reviewer
    )
    return ApiResponse(message=f"Document verification status updated to {doc.verification_status}", data=WorkerDocumentResponse.model_validate(doc))


@router.get("/workers/documents", response_model=ApiResponse[List[WorkerDocumentResponse]])
async def list_worker_documents(
    worker_id: Optional[str] = Query(None),
    contractor_id: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    docs = await worker_service.list_worker_documents(
        db=db, worker_id=worker_id, contractor_id=contractor_id, verification_status=verification_status
    )
    return ApiResponse(data=[WorkerDocumentResponse.model_validate(d) for d in docs])


# ------------------ DGMS SAFETY INDUCTION ENDPOINTS ------------------

@router.post("/workers/{worker_id}/inductions", response_model=ApiResponse[WorkerInductionResponse])
async def create_worker_induction(
    worker_id: str,
    payload: WorkerInductionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("worker.training"))
):
    induction = await worker_service.create_induction(
        db=db, worker_id=worker_id, payload=payload, user_id=current_user.email or current_user.sub
    )
    return ApiResponse(message="DGMS Safety Induction recorded successfully", data=WorkerInductionResponse.model_validate(induction))


@router.get("/workers/inductions", response_model=ApiResponse[List[WorkerInductionResponse]])
async def list_worker_inductions(
    worker_id: Optional[str] = Query(None),
    mine_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    inductions = await worker_service.list_inductions(db=db, worker_id=worker_id, mine_id=mine_id, status=status)
    return ApiResponse(data=[WorkerInductionResponse.model_validate(i) for i in inductions])


@router.get("/workers/inductions/stats", response_model=ApiResponse[WorkerInductionStats])
async def get_worker_induction_stats(
    mine_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stats = await worker_service.get_induction_stats(db=db, mine_id=mine_id)
    return ApiResponse(message="DGMS Safety Induction workforce statistics", data=stats)


# ------------------ ZONE ACCESS CLEARANCE ENDPOINT ------------------

@router.get("/workers/{worker_id}/zone-clearance", response_model=ApiResponse[WorkerZoneClearanceResponse])
async def check_worker_zone_clearance(
    worker_id: str,
    zone_id: str = Query(..., description="Restricted Zone ID e.g. ZONE-PIT-01, ZONE-BLAST-02"),
    db: AsyncSession = Depends(get_db)
):
    clearance = await worker_service.check_zone_clearance(db=db, worker_id=worker_id, zone_id=zone_id)
    return ApiResponse(message="Worker zone clearance evaluated", data=clearance)

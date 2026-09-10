"""
Contractor Management API Router (Module 3 -> Task 1)
Exposes RESTful endpoints for Contractor Registry, Contracts, Documents, Compliance, Performance & Renewals.
"""

import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, TokenPayload, require_permission
from app.models.contractor_models import Contractor, Contract, ContractDocument
from app.schemas.contractor_schemas import (
    ContractorCreate, ContractorUpdate, ContractorResponse,
    ContractCreate, ContractUpdate, ContractResponse, ContractRenewalRequest,
    ContractDocumentResponse, ContractComplianceCreate, ContractComplianceResponse,
    ContractPerformanceCreate, ContractPerformanceResponse, ContractorDashboardStats
)
from app.schemas.common_schemas import ApiResponse
from app.services.contractor_service import contractor_service

router = APIRouter(prefix="/mine", tags=["Contractor Management (Module 3)"])
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.get("/contractors/dashboard", response_model=ApiResponse[ContractorDashboardStats])
async def get_contractor_dashboard_stats(
    mine_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stats = await contractor_service.get_dashboard_stats(db=db, mine_id=mine_id)
    return ApiResponse(message="Contractor management dashboard statistics", data=stats)


@router.post("/contractors", response_model=ApiResponse[ContractorResponse])
async def create_contractor(
    payload: ContractorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.create"))
):
    contractor = await contractor_service.create_contractor(db=db, payload=payload, user_id=current_user.sub)
    return ApiResponse(message="Contractor registered successfully", data=ContractorResponse.model_validate(contractor))


@router.get("/contractors", response_model=ApiResponse[List[ContractorResponse]])
async def list_contractors(
    mine_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    compliance_status: Optional[str] = Query(None),
    work_scope: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    contractors = await contractor_service.list_contractors(
        db=db, mine_id=mine_id, status=status, search=search,
        compliance_status=compliance_status, work_scope=work_scope
    )
    return ApiResponse(data=[ContractorResponse.model_validate(c) for c in contractors])


@router.get("/contractors/{contractor_id}", response_model=ApiResponse[ContractorResponse])
async def get_contractor_details(
    contractor_id: str,
    db: AsyncSession = Depends(get_db)
):
    contractor = await contractor_service.get_contractor(db=db, contractor_id=contractor_id)
    return ApiResponse(data=ContractorResponse.model_validate(contractor))


@router.put("/contractors/{contractor_id}", response_model=ApiResponse[ContractorResponse])
async def update_contractor(
    contractor_id: str,
    payload: ContractorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.update"))
):
    contractor = await contractor_service.update_contractor(
        db=db, contractor_id=contractor_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Contractor updated successfully", data=ContractorResponse.model_validate(contractor))


@router.delete("/contractors/{contractor_id}", response_model=ApiResponse[dict])
async def delete_contractor(
    contractor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.delete"))
):
    await contractor_service.delete_contractor(db=db, contractor_id=contractor_id, user_id=current_user.sub)
    return ApiResponse(message="Contractor soft-deleted successfully", data={"id": contractor_id})


# ------------------ CONTRACT ENDPOINTS ------------------

@router.post("/contractors/{contractor_id}/contracts", response_model=ApiResponse[ContractResponse])
async def add_contract(
    contractor_id: str,
    payload: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.update"))
):
    contract = await contractor_service.add_contract(
        db=db, contractor_id=contractor_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Contract added successfully", data=ContractResponse.model_validate(contract))


@router.get("/contracts", response_model=ApiResponse[List[ContractResponse]])
async def list_contracts(
    mine_id: Optional[str] = Query(None),
    contractor_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    contracts = await contractor_service.list_contracts(
        db=db, mine_id=mine_id, contractor_id=contractor_id, status=status, contract_type=contract_type
    )
    return ApiResponse(data=[ContractResponse.model_validate(c) for c in contracts])


@router.get("/contracts/expiring", response_model=ApiResponse[List[ContractResponse]])
async def get_expiring_contracts(
    mine_id: Optional[str] = Query(None),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    contracts = await contractor_service.get_expiring_contracts(db=db, mine_id=mine_id, days=days)
    return ApiResponse(message=f"Contracts expiring within {days} days", data=[ContractResponse.model_validate(c) for c in contracts])


@router.get("/contracts/{contract_id}", response_model=ApiResponse[ContractResponse])
async def get_contract_details(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    contract = await contractor_service.get_contract(db=db, contract_id=contract_id)
    return ApiResponse(data=ContractResponse.model_validate(contract))


@router.post("/contracts/{contract_id}/renew", response_model=ApiResponse[ContractResponse])
async def renew_contract(
    contract_id: str,
    payload: ContractRenewalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.renew"))
):
    contract = await contractor_service.renew_contract(
        db=db, contract_id=contract_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Contract renewed successfully", data=ContractResponse.model_validate(contract))


# ------------------ DOCUMENT ENDPOINTS ------------------

@router.post("/contractors/{contractor_id}/documents", response_model=ApiResponse[ContractDocumentResponse])
async def upload_contractor_document(
    contractor_id: str,
    contract_id: Optional[str] = Form(None),
    document_type: str = Form(default="WORK_ORDER"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.document.upload"))
):
    file_path = os.path.join(settings.UPLOAD_DIR, f"contractor_{contractor_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    doc = await contractor_service.store_document_metadata(
        db=db,
        contractor_id=contractor_id,
        contract_id=contract_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/pdf",
        user_id=current_user.sub
    )

    return ApiResponse(message="Contractor document uploaded successfully", data=ContractDocumentResponse.model_validate(doc))


@router.get("/contractors/documents/{doc_id}/download")
async def download_contractor_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    stmt = select(ContractDocument).where(ContractDocument.id == doc_id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")

    return FileResponse(path=doc.file_path, filename=doc.file_name, media_type=doc.mime_type)


# ------------------ COMPLIANCE ENDPOINTS ------------------

@router.post("/contractors/{contractor_id}/compliance", response_model=ApiResponse[ContractComplianceResponse])
async def record_compliance_check(
    contractor_id: str,
    payload: ContractComplianceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.update"))
):
    comp = await contractor_service.record_compliance_check(
        db=db, contractor_id=contractor_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Compliance check recorded", data=ContractComplianceResponse.model_validate(comp))


# ------------------ PERFORMANCE ENDPOINTS ------------------

@router.post("/contractors/{contractor_id}/performance", response_model=ApiResponse[ContractPerformanceResponse])
async def record_performance_evaluation(
    contractor_id: str,
    payload: ContractPerformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("contractor.update"))
):
    perf = await contractor_service.record_performance_evaluation(
        db=db, contractor_id=contractor_id, payload=payload, user_id=current_user.sub
    )
    return ApiResponse(message="Performance evaluation recorded", data=ContractPerformanceResponse.model_validate(perf))

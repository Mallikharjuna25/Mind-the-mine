from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.schemas.module2_schemas import BatchSyncRequest, BatchSyncResponse
from backend.app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Sync Engine"])

@router.post("/batch", response_model=BatchSyncResponse, status_code=status.HTTP_200_OK)
def sync_batch_data(
    batch: BatchSyncRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return SyncService.process_batch(db, batch)

@router.get("/status")
def get_sync_health(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return {
        "status": "HEALTHY",
        "service": "AI MineGuard Module 2 Sync Engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database_connected": True
    }

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.routers.v1 import (
    field_reports_router,
    inspections_router,
    incidents_router,
    ai_structuring_router,
    verification_router,
    sync_router,
    media_router,
    gis_router
)

# Auto-create all tables in target database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for AI MineGuard Module 2: Field Operations & Inspection Management. Provides offline synchronization, statutory checklists, incident reporting, and assistive AI structuring."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/storage/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
api_v1 = settings.API_V1_STR
app.include_router(field_reports_router.router, prefix=api_v1)
app.include_router(inspections_router.router, prefix=api_v1)
app.include_router(incidents_router.router, prefix=api_v1)
app.include_router(ai_structuring_router.router, prefix=api_v1)
app.include_router(verification_router.router, prefix=api_v1)
app.include_router(sync_router.router, prefix=api_v1)
app.include_router(media_router.router, prefix=api_v1)
app.include_router(gis_router.router, prefix=api_v1)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "module": "Module 2 (Field Operations & Inspection Management)"}

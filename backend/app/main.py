"""
FastAPI Application Entrypoint
Mounts all Module 1 routers, CORS, global exception handlers, and database lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging_config import setup_logging, logger
from app.core.exceptions import MineGuardException, mineguard_exception_handler

# Import all models to ensure metadata registration
import app.models

# Import v1 Routers (Module 1)
from app.routers.v1.auth_router import router as auth_router
from app.routers.v1.mine_router import router as mine_router
from app.routers.v1.cctv_router import router as cctv_router
from app.routers.v1.compliance_router import router as compliance_router
from app.routers.v1.equipment_router import router as equipment_router
from app.routers.v1.environment_router import router as environment_router
from app.routers.v1.production_router import router as production_router
from app.routers.v1.risk_router import router as risk_router
from app.routers.v1.workflow_router import router as workflow_router
from app.routers.v1.demo_router import router as demo_router

# Import v1 Routers (Module 2: Field Operations & Inspection Management)
from app.routers.v1.inspections_router import router as inspections_router
from app.routers.v1.field_reports_router import router as field_reports_router
from app.routers.v1.incidents_router import router as incidents_router
from app.routers.v1.verification_router import router as verification_router
from app.routers.v1.gis_router import router as gis_router
from app.routers.v1.sync_router import router as sync_router
from app.routers.v1.ai_structuring_router import router as ai_structuring_router
from app.routers.v1.media_router import router as media_router

# Import v1 Routers (Module 3: Contractor & Worker Compliance Management)
from app.routers.v1.contractor_router import router as contractor_router
from app.routers.v1.worker_router import router as worker_router
from app.routers.v1.governance_router import router as governance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Setup logging and ensure SQLite tables are created for local development
    setup_logging(debug=settings.DEBUG)
    logger.info("Initializing AI MineGuard Backend Engine (Modules 1, 2, and 3)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified and active across all modules.")
    yield
    # Shutdown
    logger.info("Shutting down AI MineGuard Backend Engine...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Intelligent Mine Governance, Safety & Compliance Operating System (SIH26024)",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
app.add_exception_handler(MineGuardException, mineguard_exception_handler)

# Mount Module 1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(mine_router, prefix=settings.API_V1_STR)
app.include_router(cctv_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(equipment_router, prefix=settings.API_V1_STR)
app.include_router(environment_router, prefix=settings.API_V1_STR)
app.include_router(production_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(workflow_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

# Mount Module 2 Routers (Field Ops & Inspection)
app.include_router(inspections_router, prefix=settings.API_V1_STR)
app.include_router(field_reports_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(verification_router, prefix=settings.API_V1_STR)
app.include_router(gis_router, prefix=settings.API_V1_STR)
app.include_router(sync_router, prefix=settings.API_V1_STR)
app.include_router(ai_structuring_router, prefix=settings.API_V1_STR)
app.include_router(media_router, prefix=settings.API_V1_STR)

# Mount Module 3 Routers (Contractor & Worker Compliance)
app.include_router(contractor_router, prefix=settings.API_V1_STR)
app.include_router(worker_router, prefix=settings.API_V1_STR)
app.include_router(governance_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root_health_check():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "environment": settings.ENVIRONMENT,
        "modules": ["Module 1 (AI Risk & Vision)", "Module 2 (Field Ops & Inspection)", "Module 3 (Contractor & Worker Governance)"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "version": settings.PROJECT_VERSION,
        "system": settings.PROJECT_NAME
    }


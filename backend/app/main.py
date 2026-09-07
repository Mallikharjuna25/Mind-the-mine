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

# Import v1 Routers
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Setup logging and ensure SQLite tables are created for local development
    setup_logging(debug=settings.DEBUG)
    logger.info("Initializing AI MineGuard Backend Engine...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified and active.")
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

# Include Routers under API_V1_STR
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


@app.get("/")
async def root_health_check():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "environment": settings.ENVIRONMENT
    }

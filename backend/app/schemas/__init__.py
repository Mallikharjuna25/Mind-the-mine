"""
Schemas Package Initialization
"""

from app.schemas.common_schemas import ApiResponse, PaginationParams, PaginatedResponse
from app.schemas.auth_schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.schemas.mine_schemas import MineCreate, MineResponse, MineZoneCreate, MineZoneResponse
from app.schemas.cctv_schemas import CameraCreate, CameraUpdate, CameraResponse, DetectionIngestRequest, DetectionEventResponse
from app.schemas.compliance_schemas import ViolationVerifyRequest, ViolationResponse, ViolationFilterParams
from app.schemas.equipment_schemas import AssetCreate, AssetUpdate, AssetResponse, EquipmentDocumentResponse
from app.schemas.environment_schemas import EnvironmentalReadingCreate, EnvironmentalReadingResponse
from app.schemas.production_schemas import ProductionRecordCreate, ProductionRecordResponse
from app.schemas.risk_schemas import RiskScoreComputeRequest, RiskScoreResponse, AnomalyResponse, AnomalyResolveRequest
from app.schemas.workflow_schemas import AlertResponse, CorrectiveActionCreate, CorrectiveActionVerifyRequest, CorrectiveActionResponse, EscalationResponse

__all__ = [
    "ApiResponse", "PaginationParams", "PaginatedResponse",
    "LoginRequest", "TokenResponse", "UserCreate", "UserResponse",
    "MineCreate", "MineResponse", "MineZoneCreate", "MineZoneResponse",
    "CameraCreate", "CameraUpdate", "CameraResponse", "DetectionIngestRequest", "DetectionEventResponse",
    "ViolationVerifyRequest", "ViolationResponse", "ViolationFilterParams",
    "AssetCreate", "AssetUpdate", "AssetResponse", "EquipmentDocumentResponse",
    "EnvironmentalReadingCreate", "EnvironmentalReadingResponse",
    "ProductionRecordCreate", "ProductionRecordResponse",
    "RiskScoreComputeRequest", "RiskScoreResponse", "AnomalyResponse", "AnomalyResolveRequest",
    "AlertResponse", "CorrectiveActionCreate", "CorrectiveActionVerifyRequest", "CorrectiveActionResponse", "EscalationResponse"
]

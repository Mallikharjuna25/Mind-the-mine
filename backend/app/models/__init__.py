"""
SQLAlchemy Models Package Initialization
Exports all models to ensure complete metadata registration.
"""

from app.models.base import BaseModelMixin
from app.models.user_models import User
from app.models.mine_models import Mine, MineZone
from app.models.cctv_models import CameraRegistry, DetectionEvent
from app.models.compliance_models import Violation
from app.models.equipment_models import EquipmentAsset, EquipmentDocument
from app.models.environment_models import EnvironmentalReading
from app.models.production_models import ProductionRecord
from app.models.risk_models import RiskScore, Anomaly
from app.models.workflow_models import Alert, CorrectiveAction, Escalation
from app.models.audit_models import AuditLog

# Module 2: Field Operations & Inspection Management Models
from app.models.module2_models import (
    FieldReport,
    InspectionTemplate,
    InspectionAudit,
    IncidentRecord,
    AIIncidentStructuringLog,
    FieldVerification,
    AuditTrailEntry
)

# Module 3: Contractor & Worker Compliance Governance Models
from app.models.contractor_models import (
    Contractor,
    Contract,
    ContractDocument,
    ContractCompliance,
    ContractPerformance
)
from app.models.worker_models import (
    Worker,
    WorkerAttendance,
    WorkerTraining,
    WorkerCertification,
    WorkerPPE,
    WorkerAuthorization
)
from app.models.governance_models import (
    Grievance,
    GrievanceEvidence,
    GrievanceResolution,
    ApprovalRequest,
    ApprovalHistory
)

__all__ = [
    # Module 1
    "BaseModelMixin",
    "User",
    "Mine",
    "MineZone",
    "CameraRegistry",
    "DetectionEvent",
    "Violation",
    "EquipmentAsset",
    "EquipmentDocument",
    "EnvironmentalReading",
    "ProductionRecord",
    "RiskScore",
    "Anomaly",
    "Alert",
    "CorrectiveAction",
    "Escalation",
    "AuditLog",
    # Module 2
    "FieldReport",
    "InspectionTemplate",
    "InspectionAudit",
    "IncidentRecord",
    "AIIncidentStructuringLog",
    "FieldVerification",
    "AuditTrailEntry",
    # Module 3
    "Contractor",
    "Contract",
    "ContractDocument",
    "ContractCompliance",
    "ContractPerformance",
    "Worker",
    "WorkerAttendance",
    "WorkerTraining",
    "WorkerCertification",
    "WorkerPPE",
    "WorkerAuthorization",
    "Grievance",
    "GrievanceEvidence",
    "GrievanceResolution",
    "ApprovalRequest",
    "ApprovalHistory",
]


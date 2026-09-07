"""
Custom Application Exceptions & Global Exception Handlers
Provides consistent, structured JSON error responses across the API.
"""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class MineGuardException(Exception):
    """Base application exception with error code and detail"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(MineGuardException):
    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "id": str(entity_id)}
        )


class DuplicateEntityError(MineGuardException):
    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_name} with {field}='{value}' already exists.",
            code="DUPLICATE_ENTITY",
            status_code=status.HTTP_409_CONFLICT,
            details={"entity": entity_name, "field": field, "value": str(value)}
        )


class InvalidStateTransitionError(MineGuardException):
    def __init__(self, entity_name: str, current_state: str, attempted_state: str):
        super().__init__(
            message=f"Cannot transition {entity_name} from status '{current_state}' to '{attempted_state}'.",
            code="INVALID_STATE_TRANSITION",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"entity": entity_name, "from": current_state, "to": attempted_state}
        )


class OCRProcessingError(MineGuardException):
    def __init__(self, detail: str):
        super().__init__(
            message=f"OCR Processing failed: {detail}",
            code="OCR_PROCESSING_FAILURE",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"reason": detail}
        )


async def mineguard_exception_handler(request: Request, exc: MineGuardException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "path": str(request.url)
            }
        }
    )

"""
Security, Authentication & Role-Based Access Control (RBAC) Module
Provides password hashing, JWT encoding/decoding, and fine-grained permission enforcement.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Set, Any
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class UserRole:
    SUPER_ADMIN = "SUPER_ADMIN"
    MINE_MANAGER = "MINE_MANAGER"
    SAFETY_OFFICER = "SAFETY_OFFICER"
    ENVIRONMENT_OFFICER = "ENVIRONMENT_OFFICER"
    FIELD_INSPECTOR = "FIELD_INSPECTOR"
    CONTRACTOR = "CONTRACTOR"
    REGULATOR_DGMS = "REGULATOR_DGMS"
    CIL_CORPORATE = "CIL_CORPORATE"


# Standard RBAC Permission Matrix mapping roles to fine-grained scopes
ROLE_PERMISSIONS: dict[str, Set[str]] = {
    UserRole.SUPER_ADMIN: {"*"},
    UserRole.MINE_MANAGER: {
        "cctv.camera.manage", "cctv.camera.read", "cctv.detection.read",
        "compliance.violation.read", "compliance.violation.verify",
        "equipment.asset.create", "equipment.asset.read", "equipment.asset.update", "equipment.document.upload", "equipment.document.read",
        "safety.firecheck.create", "safety.firecheck.read",
        "environment.reading.create", "environment.reading.read",
        "production.record.create", "production.record.read",
        "risk.score.compute", "risk.score.read", "risk.anomaly.read", "risk.anomaly.manage",
        "alert.read", "alert.acknowledge", "action.create", "action.verify", "escalation.read"
    },
    UserRole.SAFETY_OFFICER: {
        "cctv.camera.read", "cctv.detection.read",
        "compliance.violation.read", "compliance.violation.verify",
        "equipment.asset.read", "equipment.document.read", "equipment.document.upload",
        "safety.firecheck.create", "safety.firecheck.read",
        "environment.reading.read",
        "risk.score.read", "risk.anomaly.read",
        "alert.read", "alert.acknowledge", "action.create", "action.verify", "escalation.read"
    },
    UserRole.ENVIRONMENT_OFFICER: {
        "environment.reading.create", "environment.reading.read",
        "risk.score.read", "alert.read", "alert.acknowledge"
    },
    UserRole.FIELD_INSPECTOR: {
        "cctv.camera.read", "cctv.detection.read", "compliance.violation.read",
        "equipment.asset.read", "equipment.document.upload",
        "safety.firecheck.create", "environment.reading.create",
        "alert.read", "action.verify"
    },
    UserRole.CONTRACTOR: {
        "compliance.violation.read", "equipment.asset.read", "equipment.document.upload",
        "alert.read", "action.update"
    },
    UserRole.REGULATOR_DGMS: {
        "cctv.camera.read", "cctv.detection.read", "compliance.violation.read",
        "equipment.asset.read", "equipment.document.read",
        "safety.firecheck.read", "environment.reading.read", "production.record.read",
        "risk.score.read", "risk.anomaly.read", "alert.read", "escalation.read"
    },
    UserRole.CIL_CORPORATE: {
        "cctv.camera.read", "compliance.violation.read", "equipment.asset.read",
        "safety.firecheck.read", "environment.reading.read", "production.record.read",
        "risk.score.read", "risk.anomaly.read", "alert.read", "escalation.read"
    }
}


class TokenPayload(BaseModel):
    sub: str  # user id
    email: str
    role: str
    mine_id: Optional[str] = None
    permissions: List[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes as per bcrypt specification
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing sub",
                headers={"WWW-Authenticate": "Bearer"},
            )
        role = payload.get("role", UserRole.FIELD_INSPECTOR)
        email = payload.get("email", "")
        mine_id = payload.get("mine_id")
        permissions = list(ROLE_PERMISSIONS.get(role, set()))
        return TokenPayload(sub=user_id, email=email, role=role, mine_id=mine_id, permissions=permissions)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    return decode_access_token(token)


def require_permission(permission: str):
    """
    Decorator/Dependency that enforces fine-grained permission on endpoint execution.
    SUPER_ADMIN with wildcard '*' bypasses all checks.
    """
    async def permission_checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if "*" in current_user.permissions:
            return current_user
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: missing required permission '{permission}'"
            )
        return current_user
    return permission_checker


def require_roles(allowed_roles: List[str]):
    """
    Decorator/Dependency that restricts endpoint access to specified roles.
    """
    async def role_checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role '{current_user.role}' not in allowed roles {allowed_roles}"
            )
        return current_user
    return role_checker

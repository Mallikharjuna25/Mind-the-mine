"""
Authentication Router
Endpoints for user registration, token generation (login), and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user, TokenPayload, ROLE_PERMISSIONS, UserRole
from app.models.user_models import User
from app.schemas.auth_schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.schemas.common_schemas import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        designation=payload.designation,
        phone_number=payload.phone_number,
        mine_id=payload.mine_id,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ApiResponse(message="User registered successfully", data=UserResponse.model_validate(user))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated")

    permissions = list(ROLE_PERMISSIONS.get(user.role, set()))
    token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role, "mine_id": user.mine_id})

    return ApiResponse(
        message="Login successful",
        data=TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
            mine_id=user.mine_id,
            permissions=permissions
        )
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_profile(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == current_user.sub)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ApiResponse(data=UserResponse.model_validate(user))

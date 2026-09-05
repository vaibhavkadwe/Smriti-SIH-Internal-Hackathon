"""Auth routes — register, login, refresh, logout, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.deps import _parse_sub
from app.models.user import User
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.phone == body.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        phone=body.phone,
        email=body.email,
        password_hash=AuthService.hash_password(body.password),
        role=body.role,
        preferred_language=body.preferred_language,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    if not user or not AuthService.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return TokenResponse(
        access_token=AuthService.create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=AuthService.create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a fresh access + refresh token pair."""
    payload = AuthService.verify_token(body.refresh_token)
    if payload is None or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == _parse_sub(payload["sub"])))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return TokenResponse(
        access_token=AuthService.create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=AuthService.create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Log out. JWT is stateless, so the client discards its tokens."""
    return {"status": "logged_out"}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

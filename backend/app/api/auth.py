"""
Authentication & Authorization API Routes
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Callable
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import verify_password, create_access_token, decode_access_token
from backend.app.models.users import User
from backend.app.schemas.models_schema import LoginRequest, TokenResponse, UserResponse
from backend.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/mode")
async def auth_mode():
    """Public login-screen metadata; never exposes secrets."""
    return {"dev_auth_bypass": settings.DEV_AUTH_BYPASS, "mode": "DEVELOPMENT" if settings.DEV_AUTH_BYPASS else "STANDARD"}


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency verifying JWT bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token"
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or signature invalid"
        )
    username = payload.get("sub")
    if payload.get("dev_auth_bypass") and settings.DEV_AUTH_BYPASS:
        return SimpleNamespace(
            id=f"dev-{username}", username=username,
            email=f"{username}@local.prahari", full_name=f"Development User ({username})",
            role=payload.get("role", "OPERATOR"), is_active=True,
            created_at=datetime.now(timezone.utc), last_login=datetime.now(timezone.utc),
            dev_auth_bypass=True,
        )
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*allowed_roles: str) -> Callable:
    """Create a FastAPI dependency enforcing one of the supplied roles."""
    async def role_guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions")
        return current_user
    return role_guard


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with username and password."""
    username = req.username.strip()
    password = req.password.strip()
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username and password are required")

    if settings.DEV_AUTH_BYPASS:
        normalized = username.lower()
        role = "ADMIN" if normalized == "admin" else "VIEWER" if normalized == "viewer" else "GATEWAY" if normalized == "gateway" else "OPERATOR"
        token = create_access_token({"sub": username, "role": role, "dev_auth_bypass": True})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": f"dev-{username}", "username": username,
                "email": f"{username}@local.prahari", "full_name": f"Development User ({username})",
                "role": role, "dev_auth_bypass": True,
            },
        }

    query = select(User).where(User.username == req.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Retrieve current authenticated user profile."""
    return current_user

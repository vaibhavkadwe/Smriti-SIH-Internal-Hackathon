"""Security dependency helpers."""
from typing import List, Callable
from fastapi import HTTPException, status, Depends
from app.deps import get_current_user
from app.models.all_models import User
from app.services.auth_service import AuthService

def verify_token(token: str):
    return AuthService.verify_token(token)

def require_role(*allowed_roles: str) -> Callable:
    """Build a FastAPI dependency that enforces role-based access.

    Usage:
        @router.get("/x")
        async def handler(user: User = Depends(require_role("family_caregiver", "asha_worker"))):
            ...

    Admin role is always permitted.
    """
    allowed = {role.lower() for role in allowed_roles}
    allowed.add("admin")

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if user_role.lower() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {user_role}",
            )
        return current_user

    return role_checker

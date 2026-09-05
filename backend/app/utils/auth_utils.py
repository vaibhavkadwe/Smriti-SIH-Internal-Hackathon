"""Auth and Security Utilities."""
from typing import Optional, Dict, Any
from app.services.auth_service import AuthService
from app.deps import get_current_user

def hash_password(password: str) -> str:
    return AuthService.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthService.verify_password(plain_password, hashed_password)

def create_access_token(user_id: str, role: str, extra_data: Optional[Dict[str, Any]] = None) -> str:
    data = {"sub": str(user_id), "role": role}
    if extra_data:
        data.update(extra_data)
    return AuthService.create_access_token(data)

def create_refresh_token(user_id: str) -> str:
    return AuthService.create_refresh_token({"sub": str(user_id)})

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    return AuthService.verify_token(token)

"""
Security utilities for JWT authentication
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from src.core.config import settings

# HTTP Bearer token scheme
security = HTTPBearer()


# Context para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency to get current user ID from JWT token

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or user_id not in token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get full user payload from JWT token

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        Full token payload

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    return decode_access_token(token)


def require_roles(*required_roles: str):
    """
    Dependency factory to check if user has required roles

    Args:
        required_roles: Variable number of role names required

    Returns:
        Dependency function that validates user roles

    Example:
        @router.get("/admin-only", dependencies=[Depends(require_roles("Administrador General"))])
    """
    def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        token = credentials.credentials
        payload = decode_access_token(token)

        user_roles: list = payload.get("roles", [])

        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
            )

        return payload

    return role_checker


def verify_internal_api_key(x_internal_api_key: str = Header(...)):
    """
    Dependency to verify the internal API key for service-to-service communication.
    """
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key"
        )

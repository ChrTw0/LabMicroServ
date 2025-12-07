"""
Authentication Middleware for API Gateway

This middleware validates JWT tokens and can be applied to protected routes.
For now, we'll keep it simple and let individual services handle authentication.
"""
from fastapi import Request, HTTPException, status
from typing import Optional
import jwt
from loguru import logger


class AuthMiddleware:
    """
    JWT Authentication Middleware

    NOTE: Currently optional. The backend services already validate JWT.
    This middleware can be enabled later for centralized auth validation.
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def __call__(self, request: Request):
        """Validate JWT token from Authorization header"""
        # Skip auth for public endpoints
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        if request.url.path in public_paths:
            return

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(f"No Authorization header for {request.url.path}")
            # For now, we let it pass and let backend services validate
            # Uncomment below to enforce authentication at gateway level
            # raise HTTPException(
            #     status_code=status.HTTP_401_UNAUTHORIZED,
            #     detail="Missing Authorization header"
            # )
            return

        # Parse Bearer token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                logger.warning(f"Invalid auth scheme: {scheme}")
                return
        except ValueError:
            logger.warning(f"Invalid Authorization header format")
            return

        # Validate JWT token (optional - currently disabled)
        # Uncomment to enable centralized JWT validation
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            # Attach user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.email = payload.get("email")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        """


# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public"""
    if path in PUBLIC_ENDPOINTS:
        return True
    # Auth endpoints are public
    if path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/register"):
        return True
    return False

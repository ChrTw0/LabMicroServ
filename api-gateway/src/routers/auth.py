"""
Authentication Router - Proxy to user-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login")
async def login(request: Request) -> Response:
    """
    Login - Authenticate user and get JWT token

    Request body:
    ```json
    {
        "email": "admin@lab.com",
        "password": "admin123"
    }
    ```
    """
    target_url = f"{settings.user_service_url}/api/v1/auth/login"
    return await proxy_request(request, target_url)


@router.post("/register")
async def register(request: Request) -> Response:
    """Register new user"""
    target_url = f"{settings.user_service_url}/api/v1/auth/register"
    return await proxy_request(request, target_url)


@router.get("/me")
async def get_current_user(request: Request) -> Response:
    """Get current authenticated user info"""
    target_url = f"{settings.user_service_url}/api/v1/auth/me"
    return await proxy_request(request, target_url)


@router.post("/change-password")
async def change_password(request: Request) -> Response:
    """Change password for authenticated user"""
    target_url = f"{settings.user_service_url}/api/v1/auth/change-password"
    return await proxy_request(request, target_url)


@router.post("/request-password-reset")
async def request_password_reset(request: Request) -> Response:
    """Request password reset token"""
    target_url = f"{settings.user_service_url}/api/v1/auth/request-password-reset"
    return await proxy_request(request, target_url)


@router.post("/reset-password")
async def reset_password(request: Request) -> Response:
    """Reset password with token"""
    target_url = f"{settings.user_service_url}/api/v1/auth/reset-password"
    return await proxy_request(request, target_url)


@router.post("/verify-token")
async def verify_token(request: Request) -> Response:
    """Verify JWT token validity"""
    target_url = f"{settings.user_service_url}/api/v1/auth/verify-token"
    return await proxy_request(request, target_url)

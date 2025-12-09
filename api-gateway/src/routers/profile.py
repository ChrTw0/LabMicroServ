"""
Profile Router - Proxy to user-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.get("")
async def get_my_profile(request: Request) -> Response:
    """Get current user's profile"""
    target_url = f"{settings.user_service_url}/api/v1/profile"
    return await proxy_request(request, target_url)


@router.put("")
async def update_my_profile(request: Request) -> Response:
    """Update current user's profile"""
    target_url = f"{settings.user_service_url}/api/v1/profile"
    return await proxy_request(request, target_url)


@router.put("/password")
async def change_my_password(request: Request) -> Response:
    """Change current user's password"""
    target_url = f"{settings.user_service_url}/api/v1/profile/password"
    return await proxy_request(request, target_url)

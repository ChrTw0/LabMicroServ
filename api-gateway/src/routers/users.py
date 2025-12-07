"""
Users Router - Proxy to user-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("")
async def list_users(request: Request) -> Response:
    """List all users (with pagination and filters)"""
    target_url = f"{settings.user_service_url}/api/v1/users"
    return await proxy_request(request, target_url)


@router.get("/{user_id}")
async def get_user(request: Request, user_id: int) -> Response:
    """Get user by ID"""
    target_url = f"{settings.user_service_url}/api/v1/users/{user_id}"
    return await proxy_request(request, target_url)


@router.post("")
async def create_user(request: Request) -> Response:
    """Create new user"""
    target_url = f"{settings.user_service_url}/api/v1/users"
    return await proxy_request(request, target_url)


@router.put("/{user_id}")
async def update_user(request: Request, user_id: int) -> Response:
    """Update user by ID"""
    target_url = f"{settings.user_service_url}/api/v1/users/{user_id}"
    return await proxy_request(request, target_url)


@router.delete("/{user_id}")
async def delete_user(request: Request, user_id: int) -> Response:
    """Delete user by ID"""
    target_url = f"{settings.user_service_url}/api/v1/users/{user_id}"
    return await proxy_request(request, target_url)


@router.put("/{user_id}/activate")
async def activate_user(request: Request, user_id: int) -> Response:
    """Activate user"""
    target_url = f"{settings.user_service_url}/api/v1/users/{user_id}/activate"
    return await proxy_request(request, target_url)


@router.put("/{user_id}/deactivate")
async def deactivate_user(request: Request, user_id: int) -> Response:
    """Deactivate user"""
    target_url = f"{settings.user_service_url}/api/v1/users/{user_id}/deactivate"
    return await proxy_request(request, target_url)

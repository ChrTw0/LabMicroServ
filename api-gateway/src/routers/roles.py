"""
Roles Router - Proxy to user-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.get("")
async def list_roles(request: Request) -> Response:
    """List all roles"""
    target_url = f"{settings.user_service_url}/api/v1/roles"
    return await proxy_request(request, target_url)


@router.get("/available-permissions")
async def get_available_permissions(request: Request) -> Response:
    """List all available permissions"""
    target_url = f"{settings.user_service_url}/api/v1/roles/available-permissions"
    return await proxy_request(request, target_url)


@router.get("/{role_id}")
async def get_role(request: Request, role_id: int) -> Response:
    """Get role by ID"""
    target_url = f"{settings.user_service_url}/api/v1/roles/{role_id}"
    return await proxy_request(request, target_url)


@router.post("")
async def create_role(request: Request) -> Response:
    """Create new role"""
    target_url = f"{settings.user_service_url}/api/v1/roles"
    return await proxy_request(request, target_url)


@router.put("/{role_id}")
async def update_role(request: Request, role_id: int) -> Response:
    """Update role by ID"""
    target_url = f"{settings.user_service_url}/api/v1/roles/{role_id}"
    return await proxy_request(request, target_url)


@router.delete("/{role_id}")
async def delete_role(request: Request, role_id: int) -> Response:
    """Delete role by ID"""
    target_url = f"{settings.user_service_url}/api/v1/roles/{role_id}"
    return await proxy_request(request, target_url)

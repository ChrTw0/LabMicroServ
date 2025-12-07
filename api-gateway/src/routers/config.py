"""
Configuration Router - Proxy to configuration-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/configuration", tags=["Configuration"])


# ============================================
# LOCATIONS (SEDES) ENDPOINTS
# ============================================

@router.get("/locations", tags=["Locations"])
async def list_locations(request: Request) -> Response:
    """List all locations/sedes"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/locations"
    return await proxy_request(request, target_url)


@router.get("/locations/{location_id}", tags=["Locations"])
async def get_location(request: Request, location_id: int) -> Response:
    """Get location by ID"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/locations/{location_id}"
    return await proxy_request(request, target_url)


@router.post("/locations", tags=["Locations"])
async def create_location(request: Request) -> Response:
    """Create new location"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/locations"
    return await proxy_request(request, target_url)


@router.put("/locations/{location_id}", tags=["Locations"])
async def update_location(request: Request, location_id: int) -> Response:
    """Update location by ID"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/locations/{location_id}"
    return await proxy_request(request, target_url)


@router.delete("/locations/{location_id}", tags=["Locations"])
async def delete_location(request: Request, location_id: int) -> Response:
    """Delete location by ID"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/locations/{location_id}"
    return await proxy_request(request, target_url)


# ============================================
# COMPANY DATA ENDPOINTS
# ============================================

@router.get("/company", tags=["Company"])
async def get_company_data(request: Request) -> Response:
    """Get company data (RUC, razón social, logo)"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/company"
    return await proxy_request(request, target_url)


@router.post("/company", tags=["Company"])
async def create_company_data(request: Request) -> Response:
    """Create company data"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/company"
    return await proxy_request(request, target_url)


@router.put("/company/{company_id}", tags=["Company"])
async def update_company_data(request: Request, company_id: int) -> Response:
    """Update company data"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/company/{company_id}"
    return await proxy_request(request, target_url)


# ============================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================

@router.get("/settings", tags=["Settings"])
async def list_settings(request: Request) -> Response:
    """List all system settings"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings"
    return await proxy_request(request, target_url)


@router.get("/settings/{key}", tags=["Settings"])
async def get_setting(request: Request, key: str) -> Response:
    """Get setting by key"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings/{key}"
    return await proxy_request(request, target_url)


@router.post("/settings", tags=["Settings"])
async def create_setting(request: Request) -> Response:
    """Create new setting"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings"
    return await proxy_request(request, target_url)


@router.put("/settings/{key}", tags=["Settings"])
async def update_setting(request: Request, key: str) -> Response:
    """Update setting by key"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings/{key}"
    return await proxy_request(request, target_url)


@router.delete("/settings/{key}", tags=["Settings"])
async def delete_setting(request: Request, key: str) -> Response:
    """Delete setting by key"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings/{key}"
    return await proxy_request(request, target_url)


@router.put("/settings/{key}/upsert", tags=["Settings"])
async def upsert_setting(request: Request, key: str) -> Response:
    """Create or update setting (upsert)"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings/{key}/upsert"
    return await proxy_request(request, target_url)


@router.post("/settings/bulk", tags=["Settings"])
async def bulk_update_settings(request: Request) -> Response:
    """Bulk create/update multiple settings"""
    target_url = f"{settings.configuration_service_url}/api/v1/configuration/settings/bulk"
    return await proxy_request(request, target_url)

"""
Reconciliation Router - Proxy to billing-service reconciliation module
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/reconciliation", tags=["Reconciliation"])


# ============================================
# DAILY CLOSURE ENDPOINTS
# ============================================

@router.get("/closures")
async def list_closures(request: Request) -> Response:
    """List all daily closures (with pagination and filters) - RF-062"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures"
    return await proxy_request(request, target_url)


@router.get("/closures/statistics")
async def get_closure_statistics(request: Request) -> Response:
    """Get closure statistics"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures/statistics"
    return await proxy_request(request, target_url)


@router.get("/closures/{closure_id}")
async def get_closure_by_id(request: Request, closure_id: int) -> Response:
    """Get closure by ID with discrepancies"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures/{closure_id}"
    return await proxy_request(request, target_url)


@router.post("/closures")
async def create_daily_closure(request: Request) -> Response:
    """Create daily closure and perform reconciliation - RF-056, RF-057, RF-058"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures"
    return await proxy_request(request, target_url)


@router.put("/closures/{closure_id}/close")
async def close_daily_closure(request: Request, closure_id: int) -> Response:
    """Close a daily closure"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures/{closure_id}/close"
    return await proxy_request(request, target_url)


@router.post("/closures/{closure_id}/reopen")
async def reopen_closure(request: Request, closure_id: int) -> Response:
    """Reopen a closed closure - RF-063 (admin only)"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures/{closure_id}/reopen"
    return await proxy_request(request, target_url)


# ============================================
# DISCREPANCY ENDPOINTS
# ============================================

@router.post("/closures/{closure_id}/discrepancies")
async def add_discrepancy(request: Request, closure_id: int) -> Response:
    """Add manual discrepancy to closure"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/closures/{closure_id}/discrepancies"
    return await proxy_request(request, target_url)


@router.put("/discrepancies/{discrepancy_id}/resolve")
async def resolve_discrepancy(request: Request, discrepancy_id: int) -> Response:
    """Mark discrepancy as resolved"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/discrepancies/{discrepancy_id}/resolve"
    return await proxy_request(request, target_url)


# ============================================
# RECONCILIATION REPORT ENDPOINTS
# ============================================

@router.get("/report")
async def get_reconciliation_report(request: Request) -> Response:
    """Generate complete reconciliation report - RF-057, RF-059"""
    target_url = f"{settings.billing_service_url}/api/v1/reconciliation/report"
    return await proxy_request(request, target_url)

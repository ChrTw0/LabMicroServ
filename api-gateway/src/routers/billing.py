"""
Billing Router - Proxy to billing-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/invoices", tags=["Billing"])


@router.get("")
async def list_invoices(request: Request) -> Response:
    """List all invoices/comprobantes (with pagination and filters)"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices"
    return await proxy_request(request, target_url)


@router.get("/statistics")
async def get_billing_statistics(request: Request) -> Response:
    """Get billing statistics"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/statistics"
    return await proxy_request(request, target_url)


@router.get("/{invoice_id}")
async def get_invoice(request: Request, invoice_id: int) -> Response:
    """Get invoice by ID"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}"
    return await proxy_request(request, target_url)


@router.post("")
async def create_invoice(request: Request) -> Response:
    """
    Create invoice (Boleta or Factura)

    Automatically determines type based on document:
    - DNI -> BOLETA
    - RUC -> FACTURA
    """
    target_url = f"{settings.billing_service_url}/api/v1/invoices"
    return await proxy_request(request, target_url)


@router.put("/{invoice_id}")
async def update_invoice(request: Request, invoice_id: int) -> Response:
    """Update invoice by ID"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}"
    return await proxy_request(request, target_url)


@router.delete("/{invoice_id}")
async def cancel_invoice(request: Request, invoice_id: int) -> Response:
    """Cancel/annul invoice"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}"
    return await proxy_request(request, target_url)


@router.put("/{invoice_id}/status")
async def update_invoice_status(request: Request, invoice_id: int) -> Response:
    """Update invoice status"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}/status"
    return await proxy_request(request, target_url)


# ============================================
# SUNAT INTEGRATION ENDPOINTS
# ============================================

@router.get("/{invoice_id}/ubl")
async def get_invoice_ubl_xml(request: Request, invoice_id: int) -> Response:
    """Get UBL XML of invoice"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}/ubl"
    return await proxy_request(request, target_url)


@router.get("/{invoice_id}/cdr")
async def get_invoice_cdr(request: Request, invoice_id: int) -> Response:
    """Get CDR (Constancia de Recepción) from SUNAT"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}/cdr"
    return await proxy_request(request, target_url)


@router.get("/{invoice_id}/tributary-status")
async def get_invoice_tributary_status(request: Request, invoice_id: int) -> Response:
    """Check invoice tributary status with SUNAT"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}/tributary-status"
    return await proxy_request(request, target_url)


@router.post("/{invoice_id}/resend")
async def resend_invoice_email(request: Request, invoice_id: int) -> Response:
    """Resend invoice by email"""
    target_url = f"{settings.billing_service_url}/api/v1/invoices/{invoice_id}/resend"
    return await proxy_request(request, target_url)

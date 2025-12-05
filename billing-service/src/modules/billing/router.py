"""
Billing Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
import base64

from src.core.database import get_db
from src.modules.billing.service import InvoiceService
from src.modules.billing.schemas import (
    InvoiceCreate, InvoiceUpdateStatus,
    InvoiceResponse, InvoiceDetailResponse, InvoiceListResponse, InvoiceStats
)
from src.modules.billing.models import InvoiceType, InvoiceStatus
from src.utils.sunat_client import build_ubl_invoice_xml, sign_xml_placeholder, create_zip_from_xml

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])

# ------------------------------
# ENDPOINTS EXISTENTES
# ------------------------------

@router.get(
    "",
    response_model=InvoiceListResponse,
    summary="Listar todos los comprobantes"
)
async def get_all_invoices(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por número, cliente o documento"),
    invoice_type: Optional[InvoiceType] = Query(None, description="Filtrar por tipo (BOLETA/FACTURA)"),
    invoice_status: Optional[InvoiceStatus] = Query(None, description="Filtrar por estado"),
    patient_id: Optional[int] = Query(None, description="Filtrar por ID de paciente"),
    location_id: Optional[int] = Query(None, description="Filtrar por ID de sede"),
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    return await InvoiceService.get_all_invoices(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        invoice_type=invoice_type,
        invoice_status=invoice_status,
        patient_id=patient_id,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to
    )


@router.get(
    "/statistics",
    response_model=InvoiceStats,
    summary="Obtener estadísticas de facturación"
)
async def get_statistics(
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    return await InvoiceService.get_statistics(db, date_from, date_to)


@router.get(
    "/order/{order_id}",
    response_model=InvoiceDetailResponse,
    summary="Buscar comprobante por orden"
)
async def get_invoice_by_order(order_id: int, db: AsyncSession = Depends(get_db)):
    return await InvoiceService.get_invoice_by_order(db, order_id)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetailResponse,
    summary="Obtener comprobante por ID"
)
async def get_invoice_by_id(invoice_id: int, db: AsyncSession = Depends(get_db)):
    return await InvoiceService.get_invoice_by_id(db, invoice_id)


@router.post(
    "",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar comprobante desde orden"
)
async def create_invoice_from_order(data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    return await InvoiceService.create_invoice_from_order(db, data)


@router.put(
    "/{invoice_id}/status",
    response_model=InvoiceResponse,
    summary="Actualizar estado de comprobante"
)
async def update_invoice_status(invoice_id: int, data: InvoiceUpdateStatus, db: AsyncSession = Depends(get_db)):
    return await InvoiceService.update_invoice_status(db, invoice_id, data)


@router.delete(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Anular comprobante"
)
async def cancel_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    return await InvoiceService.cancel_invoice(db, invoice_id)

# ------------------------------
# NUEVOS ENDPOINTS TRIBUTARIOS
# ------------------------------

@router.get("/{invoice_id}/ubl", summary="Obtener XML UBL generado")
async def get_invoice_ubl(invoice_id: int, db: AsyncSession = Depends(get_db)):
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    xml = build_ubl_invoice_xml(invoice)
    return {"invoice_id": invoice_id, "xml": xml}


@router.get("/{invoice_id}/cdr", summary="Obtener CDR devuelto por SUNAT")
async def get_invoice_cdr(invoice_id: int, db: AsyncSession = Depends(get_db)):
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    cdr_bytes = b""  # placeholder si aún no se persiste CDR real
    cdr_b64 = base64.b64encode(cdr_bytes).decode("utf-8")
    return {"invoice_id": invoice_id, "cdr": cdr_b64}


@router.get("/{invoice_id}/tributary-status", summary="Obtener estado tributario completo")
async def get_tributary_status(invoice_id: int, db: AsyncSession = Depends(get_db)):
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.invoice_status
    }


@router.post("/{invoice_id}/resend", summary="Reenviar comprobante a SUNAT")
async def resend_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    result = await InvoiceService.generate_and_send_to_sunat(db, invoice_id)
    return {
        "invoice_id": invoice_id,
        "invoice_number": result.invoice_number,
        "status": result.invoice_status
    }

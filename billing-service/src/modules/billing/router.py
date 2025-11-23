"""
Billing Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from src.core.database import get_db
from src.modules.billing.service import InvoiceService
from src.modules.billing.schemas import (
    InvoiceCreate, InvoiceUpdateStatus,
    InvoiceResponse, InvoiceDetailResponse, InvoiceListResponse, InvoiceStats
)
from src.modules.billing.models import InvoiceType, InvoiceStatus

# Note: Authentication will be added later when integrating with user-service
# For now, endpoints are public for testing

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])


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
    """
    Obtener lista paginada de comprobantes con filtros

    **Filtros disponibles:**
    - **search**: Busca por número de comprobante, nombre de cliente o documento
    - **invoice_type**: BOLETA o FACTURA
    - **invoice_status**: DRAFT, PENDING, SENT, ACCEPTED, REJECTED, CANCELLED
    - **patient_id**: Filtra por paciente
    - **location_id**: Filtra por sede
    - **date_from**: Fecha desde
    - **date_to**: Fecha hasta
    """
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
    """
    Obtener estadísticas de facturación

    - Total de comprobantes
    - Comprobantes por tipo (BOLETA/FACTURA)
    - Comprobantes por estado
    - Total facturado (solo comprobantes aceptados)
    """
    return await InvoiceService.get_statistics(db, date_from, date_to)


@router.get(
    "/order/{order_id}",
    response_model=InvoiceDetailResponse,
    summary="Buscar comprobante por orden"
)
async def get_invoice_by_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar comprobante asociado a una orden

    Útil para verificar si una orden ya tiene comprobante generado
    """
    return await InvoiceService.get_invoice_by_order(db, order_id)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetailResponse,
    summary="Obtener comprobante por ID"
)
async def get_invoice_by_id(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de un comprobante específico

    Incluye:
    - Items del comprobante
    - Datos del cliente
    - Montos (subtotal, impuestos, total)
    """
    return await InvoiceService.get_invoice_by_id(db, invoice_id)


@router.post(
    "",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar comprobante desde orden"
)
async def create_invoice_from_order(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Generar un comprobante (Boleta o Factura) a partir de una orden

    **Proceso:**
    1. Valida que la orden exista
    2. Valida que no exista ya un comprobante para esa orden
    3. Obtiene datos del paciente
    4. Valida el tipo de comprobante según documento del cliente:
       - BOLETA: Para DNI
       - FACTURA: Solo para RUC
    5. Genera número correlativo automático (B001-00000001 o F001-00000001)
    6. Crea el comprobante con los items de la orden

    **Campos:**
    - **order_id**: ID de la orden (debe estar completada)
    - **invoice_type**: BOLETA o FACTURA
    """
    return await InvoiceService.create_invoice_from_order(db, data)


@router.put(
    "/{invoice_id}/status",
    response_model=InvoiceResponse,
    summary="Actualizar estado de comprobante"
)
async def update_invoice_status(
    invoice_id: int,
    data: InvoiceUpdateStatus,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar estado de un comprobante

    **Estados disponibles:**
    - DRAFT: Borrador
    - PENDING: Pendiente de envío
    - SENT: Enviado a SUNAT
    - ACCEPTED: Aceptado por SUNAT
    - REJECTED: Rechazado por SUNAT
    - CANCELLED: Anulado

    **Restricción:** No se puede cambiar el estado de un comprobante anulado
    """
    return await InvoiceService.update_invoice_status(db, invoice_id, data)


@router.delete(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Anular comprobante"
)
async def cancel_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Anular un comprobante

    **Nota:**
    - Cambia el estado a CANCELLED
    - No se elimina físicamente el comprobante
    - Un comprobante anulado no puede cambiar de estado
    """
    return await InvoiceService.cancel_invoice(db, invoice_id)

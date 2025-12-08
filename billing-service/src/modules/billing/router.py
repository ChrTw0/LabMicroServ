"""
Billing Router - API endpoints completos para operaciones de facturación
Incluye endpoints CRUD + tributarios (UBL, CDR, envío SUNAT)
"""
from fastapi import APIRouter, Depends, status, Query, Path, Body
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

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])


# ========================================
# ENDPOINTS CRUD BÁSICOS
# ========================================

@router.get(
    "",
    response_model=InvoiceListResponse,
    summary="Listar todos los comprobantes",
    description="Obtiene lista paginada de comprobantes con múltiples filtros"
)
async def get_all_invoices(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=200, description="Tamaño de página (máx 200)"),
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
    Lista comprobantes con filtros opcionales:
    - Paginación configurable
    - Búsqueda por texto en número/cliente/documento
    - Filtros por tipo, estado, paciente, sede
    - Rango de fechas
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
    summary="Obtener estadísticas de facturación",
    description="Retorna métricas agregadas de facturación en un rango de fechas"
)
async def get_statistics(
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Estadísticas incluyen:
    - Total facturado
    - Cantidad de comprobantes por tipo/estado
    - Montos por categoría
    """
    return await InvoiceService.get_statistics(db, date_from, date_to)


@router.get(
    "/order/{order_id}",
    response_model=InvoiceDetailResponse,
    summary="Buscar comprobante por orden",
    description="Obtiene el comprobante asociado a una orden específica"
)
async def get_invoice_by_order(
    order_id: int = Path(..., gt=0, description="ID de la orden"),
    db: AsyncSession = Depends(get_db)
):
    """Busca el comprobante generado para una orden. Retorna 404 si no existe."""
    return await InvoiceService.get_invoice_by_order(db, order_id)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetailResponse,
    summary="Obtener comprobante por ID",
    description="Obtiene detalle completo de un comprobante incluyendo items"
)
async def get_invoice_by_id(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante"),
    db: AsyncSession = Depends(get_db)
):
    """Retorna detalle completo del comprobante con todos sus items."""
    return await InvoiceService.get_invoice_by_id(db, invoice_id)


@router.post(
    "",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar comprobante desde orden",
    description="Crea un comprobante electrónico a partir de una orden existente"
)
async def create_invoice_from_order(
    data: InvoiceCreate = Body(..., description="Datos para generar el comprobante"),
    send_now: bool = Query(False, description="Si True, envía inmediatamente a SUNAT"),
    db: AsyncSession = Depends(get_db)
):
    """
    Flujo de creación:
    1. Valida que no exista comprobante para la orden
    2. Consulta datos de la orden (order-service)
    3. Consulta datos del paciente (patient-service)
    4. Valida tipo de documento según tipo de comprobante
    5. Calcula montos (subtotal, IGV, total)
    6. Genera número correlativo
    7. Persiste comprobante e items
    8. Opcionalmente envía a SUNAT si send_now=True
    """
    return await InvoiceService.create_invoice_from_order(db, data, send_now)


@router.patch(
    "/{invoice_id}/status",
    response_model=InvoiceResponse,
    summary="Actualizar estado de comprobante",
    description="Modifica el estado de un comprobante (no permite modificar anulados)"
)
async def update_invoice_status(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante"),
    data: InvoiceUpdateStatus = Body(..., description="Nuevo estado"),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el estado. Rechaza cambios en comprobantes anulados."""
    return await InvoiceService.update_invoice_status(db, invoice_id, data)


@router.post(
    "/{invoice_id}/cancel",
    response_model=InvoiceResponse,
    summary="Anular comprobante",
    description="Marca un comprobante como CANCELLED (operación irreversible)"
)
async def cancel_invoice(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante a anular"),
    db: AsyncSession = Depends(get_db)
):
    """
    Anula un comprobante cambiando su estado a CANCELLED.
    Esta operación es permanente y no se puede revertir.
    """
    return await InvoiceService.cancel_invoice(db, invoice_id)


# ========================================
# ENDPOINTS TRIBUTARIOS (SUNAT)
# ========================================

@router.get(
    "/{invoice_id}/ubl",
    summary="Obtener XML UBL generado",
    description="Retorna el XML UBL 2.1 del comprobante (sin firmar)"
)
async def get_invoice_ubl(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante"),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera y retorna el XML UBL del comprobante.
    Útil para inspección o debugging antes del envío a SUNAT.
    """
    from src.modules.billing.service import build_ubl_invoice_xml
    from src.modules.billing.repository import InvoiceRepository
    
    invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
    if not invoice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Comprobante {invoice_id} no encontrado")
    
    xml = build_ubl_invoice_xml(invoice)
    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice.invoice_number,
        "xml": xml
    }


@router.get(
    "/{invoice_id}/cdr",
    summary="Obtener CDR (Constancia de Recepción)",
    description="Retorna el CDR devuelto por SUNAT después del envío"
)
async def get_invoice_cdr(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el CDR (Constancia de Recepción) devuelto por SUNAT.
    Si aún no se ha enviado o no hay CDR, retorna vacío.
    
    TODO: Implementar almacenamiento de CDR en base de datos o filesystem.
    """
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    
    # Placeholder - agregar campo cdr_zip en modelo para persistencia real
    cdr_bytes = b""  # Recuperar de invoice.cdr_zip cuando esté implementado
    cdr_b64 = base64.b64encode(cdr_bytes).decode("utf-8") if cdr_bytes else None
    
    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.invoice_status,
        "cdr_base64": cdr_b64,
        "has_cdr": bool(cdr_bytes)
    }


@router.get(
    "/{invoice_id}/tributary-status",
    summary="Obtener estado tributario completo",
    description="Retorna el estado tributario del comprobante ante SUNAT"
)
async def get_tributary_status(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna información tributaria completa:
    - Estado actual del comprobante
    - Número de comprobante
    - Fechas relevantes
    - Información de envío a SUNAT (si aplica)
    """
    invoice = await InvoiceService.get_invoice_by_id(db, invoice_id)
    
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_type": invoice.invoice_type,
        "status": invoice.invoice_status,
        "issue_date": invoice.issue_date,
        "created_at": invoice.created_at,
        "can_send_to_sunat": invoice.invoice_status in [
            InvoiceStatus.PENDING,
            InvoiceStatus.REJECTED
        ],
        "can_cancel": invoice.invoice_status != InvoiceStatus.CANCELLED
    }


@router.post(
    "/{invoice_id}/send-sunat",
    response_model=InvoiceDetailResponse,
    summary="Enviar/Reenviar comprobante a SUNAT",
    description="Genera XML, firma, empaqueta y envía el comprobante a SUNAT"
)
async def send_invoice_to_sunat(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante a enviar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Flujo completo de envío a SUNAT:
    1. Carga comprobante con items
    2. Genera XML UBL 2.1
    3. Firma digitalmente el XML (XAdES-BES)
    4. Empaqueta en ZIP
    5. Envía a SUNAT vía web service
    6. Procesa CDR (Constancia de Recepción)
    7. Actualiza estado del comprobante
    8. Envía email al cliente con adjuntos (si SMTP configurado)
    
    Se puede usar tanto para envío inicial como para reenvío en caso de rechazo.
    """
    result = await InvoiceService.generate_and_send_to_sunat(db, invoice_id)
    return result


@router.post(
    "/{invoice_id}/resend",
    response_model=InvoiceDetailResponse,
    summary="Reenviar comprobante a SUNAT (alias)",
    description="Alias del endpoint send-sunat para reenvío explícito"
)
async def resend_invoice_to_sunat(
    invoice_id: int = Path(..., gt=0, description="ID del comprobante a reenviar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint alias para claridad semántica al reenviar un comprobante.
    Funcionalidad idéntica a /send-sunat.
    """
    result = await InvoiceService.generate_and_send_to_sunat(db, invoice_id)
    return result
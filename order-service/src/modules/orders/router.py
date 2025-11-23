"""
Order Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from src.core.database import get_db
from src.modules.orders.service import OrderService
from src.modules.orders.schemas import (
    OrderCreate, OrderUpdate, OrderUpdateStatus, OrderAddPayment,
    OrderResponse, OrderDetailResponse, OrderListResponse, OrderStats
)
from src.modules.orders.models import OrderStatus

# Note: Authentication will be added later when integrating with user-service
# For now, endpoints are public for testing

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.get(
    "",
    response_model=OrderListResponse,
    summary="Listar todas las órdenes"
)
async def get_all_orders(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por número de orden"),
    patient_id: Optional[int] = Query(None, description="Filtrar por ID de paciente"),
    location_id: Optional[int] = Query(None, description="Filtrar por ID de sede"),
    status: Optional[OrderStatus] = Query(None, description="Filtrar por estado"),
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista paginada de órdenes con filtros

    **Filtros disponibles:**
    - **search**: Busca por número de orden
    - **patient_id**: Filtra por paciente
    - **location_id**: Filtra por sede
    - **status**: Filtra por estado (REGISTRADA, EN_PROCESO, COMPLETADA, ANULADA)
    - **date_from**: Fecha desde
    - **date_to**: Fecha hasta
    """
    return await OrderService.get_all_orders(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        patient_id=patient_id,
        location_id=location_id,
        status=status,
        date_from=date_from,
        date_to=date_to
    )


@router.get(
    "/statistics",
    response_model=OrderStats,
    summary="Obtener estadísticas de órdenes"
)
async def get_statistics(
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas de órdenes

    - Total de órdenes
    - Órdenes por estado
    - Ingresos totales (solo órdenes completadas)
    """
    return await OrderService.get_statistics(db, date_from, date_to)


@router.get(
    "/number/{order_number}",
    response_model=OrderDetailResponse,
    summary="Buscar orden por número"
)
async def get_order_by_number(
    order_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar orden por número de orden

    Útil para buscar rápidamente una orden específica
    """
    return await OrderService.get_order_by_number(db, order_number)


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Obtener orden por ID"
)
async def get_order_by_id(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de una orden específica

    Incluye:
    - Items (servicios) de la orden
    - Pagos realizados
    - Total pagado
    - Saldo pendiente
    """
    return await OrderService.get_order_by_id(db, order_id)


@router.post(
    "",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva orden"
)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva orden en el sistema

    **Proceso:**
    1. Se valida que el paciente exista
    2. Se validan todos los servicios
    3. Se calculan automáticamente los subtotales y total
    4. Se genera un número de orden único (ORD-YYYYMMDD-XXXX)
    5. Se crea la orden en estado REGISTRADA

    **Campos:**
    - **patient_id**: ID del paciente (debe existir en patient-service)
    - **location_id**: ID de la sede
    - **items**: Lista de servicios (mínimo 1)
      - **service_id**: ID del servicio del catálogo
      - **quantity**: Cantidad (default: 1)
    """
    return await OrderService.create_order(db, data)


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Actualizar orden"
)
async def update_order(
    order_id: int,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar orden (solo sede)

    **Nota:**
    - Solo se puede actualizar la sede (location_id)
    - No se puede modificar si está COMPLETADA o ANULADA
    """
    return await OrderService.update_order(db, order_id, data)


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Actualizar estado de orden"
)
async def update_order_status(
    order_id: int,
    data: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar estado de una orden

    **Flujo de estados:**
    - REGISTRADA → EN_PROCESO → COMPLETADA
    - Cualquier estado → ANULADA

    **Restricciones:**
    - No se puede cambiar el estado de una orden ANULADA
    - Una orden COMPLETADA solo puede ser ANULADA
    """
    return await OrderService.update_order_status(db, order_id, data)


@router.post(
    "/{order_id}/payments",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar pago a orden"
)
async def add_payment_to_order(
    order_id: int,
    data: OrderAddPayment,
    db: AsyncSession = Depends(get_db)
):
    """
    Agregar uno o más pagos a una orden

    **Características:**
    - Soporta múltiples pagos (pago parcial)
    - Valida que no se exceda el saldo pendiente
    - No permite pagos en órdenes ANULADAS

    **Métodos de pago:**
    - EFECTIVO
    - TARJETA
    - TRANSFERENCIA
    - YAPE_PLIN

    **Ejemplo:** Una orden de S/ 100 puede tener:
    - Pago 1: S/ 50 en EFECTIVO
    - Pago 2: S/ 30 en YAPE_PLIN
    - Pago 3: S/ 20 en TARJETA
    """
    return await OrderService.add_payment_to_order(db, order_id, data)


@router.delete(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Anular orden"
)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Anular una orden

    **Nota:**
    - Cambia el estado a ANULADA
    - No se elimina físicamente la orden
    - Una orden anulada no puede cambiar de estado
    """
    return await OrderService.cancel_order(db, order_id)

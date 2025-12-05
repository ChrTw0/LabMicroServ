from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.core.database import get_db
# from src.core.security import get_current_user_id, require_roles
from . import service
from . import schemas

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
    # dependencies=[Depends(require_roles("Administrador General", "Supervisor de Sede", "Recepcionista"))]
)

# Mock user ID for development until security is integrated
def get_current_user_id():
    return 1

admin_supervisor_roles = [] # Depends(require_roles("Administrador General", "Supervisor de Sede"))

@router.post("", response_model=schemas.OrderDetailResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva orden")
async def create_order(
    data: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Crea una nueva orden de laboratorio.
    - Valida que las pruebas existan en el catálogo.
    - Calcula el monto total y final.
    - Asocia los items de prueba a la orden.
    - **Requiere rol:** Recepcionista, Supervisor, Admin.
    """
    return await service.create_order(db, data, user_id)

@router.get("", response_model=schemas.OrderListResponse, summary="Listar órdenes")
async def get_all_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    status: Optional[schemas.OrderStatus] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista paginada de órdenes.
    - Permite filtrar por paciente y estado.
    """
    return await service.get_all_orders(db, page, page_size, patient_id, status)

@router.get("/{order_id}", response_model=schemas.OrderDetailResponse, summary="Obtener orden por ID")
async def get_order_by_id(order_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene los detalles completos de una orden, incluyendo sus items.
    """
    order = await service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=schemas.OrderDetailResponse, summary="Actualizar orden", dependencies=admin_supervisor_roles)
async def update_order(
    order_id: int,
    data: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza información básica de una orden (ej. nombre del médico referente).
    - **Requiere rol:** Supervisor, Admin.
    """
    updated_order = await service.update_order(db, order_id, data)
    if not updated_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return updated_order

@router.delete("/{order_id}", response_model=schemas.OrderDetailResponse, summary="Cancelar orden", dependencies=admin_supervisor_roles)
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """
    Cancela una orden (cambia su estado a CANCELLED).
    - No elimina el registro.
    - **Requiere rol:** Supervisor, Admin.
    """
    cancelled_order = await service.cancel_order(db, order_id)
    if not cancelled_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or cannot be cancelled")
    return cancelled_order

@router.put("/{order_id}/status", response_model=schemas.OrderDetailResponse, summary="Cambiar estado de la orden", dependencies=admin_supervisor_roles)
async def update_order_status(
    order_id: int,
    data: schemas.OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza el estado de una orden (Pendiente, En Proceso, Completada).
    - Valida las transiciones de estado permitidas.
    - **Requiere rol:** Supervisor, Admin.
    """
    updated_order = await service.update_order_status(db, order_id, data.status)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found or status transition not allowed")
    return updated_order

@router.post("/{order_id}/payments", response_model=schemas.OrderDetailResponse, summary="Registrar pago en una orden")
async def add_payment_to_order(
    order_id: int,
    payment: schemas.OrderPaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Añade un pago a una orden existente.
    - Valida que el monto del pago no exceda el saldo pendiente.
    """
    order_with_payment = await service.add_payment(db, order_id, payment)
    if not order_with_payment:
        raise HTTPException(status_code=404, detail="Order not found or payment exceeds balance")
    return order_with_payment
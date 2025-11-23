"""
Lab Integration Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.modules.lab_integration.service import LabSyncService
from src.modules.lab_integration.schemas import (
    LabSyncRequest, LabSyncResponse, LabSyncListResponse, LabSyncStats
)
from src.modules.lab_integration.models import SyncStatus

# Note: Authentication will be added later when integrating with user-service
# For now, endpoints are public for testing

router = APIRouter(prefix="/api/v1/lab-sync", tags=["Lab Integration"])


@router.get(
    "",
    response_model=LabSyncListResponse,
    summary="Listar logs de sincronización LIS"
)
async def get_all_sync_logs(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    sync_status: Optional[SyncStatus] = Query(None, description="Filtrar por estado de sincronización"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista paginada de logs de sincronización con el LIS

    **Filtros disponibles:**
    - **sync_status**: PENDING, SUCCESS, FAILED
    """
    return await LabSyncService.get_all_sync_logs(
        db=db,
        page=page,
        page_size=page_size,
        sync_status=sync_status
    )


@router.get(
    "/statistics",
    response_model=LabSyncStats,
    summary="Obtener estadísticas de sincronización"
)
async def get_sync_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas de sincronización con el LIS

    - Total de sincronizaciones
    - Sincronizaciones por estado (PENDING, SUCCESS, FAILED)
    - Total de sincronizaciones fallidas
    """
    return await LabSyncService.get_statistics(db)


@router.get(
    "/order/{order_id}",
    response_model=LabSyncResponse,
    summary="Obtener log de sincronización por orden"
)
async def get_sync_log_by_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener log de sincronización asociado a una orden específica

    Útil para verificar si una orden ya fue sincronizada con el LIS
    """
    return await LabSyncService.get_sync_log_by_order(db, order_id)


@router.get(
    "/{log_id}",
    response_model=LabSyncResponse,
    summary="Obtener log de sincronización por ID"
)
async def get_sync_log_by_id(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles de un log de sincronización específico
    """
    return await LabSyncService.get_sync_log_by_id(db, log_id)


@router.post(
    "",
    response_model=LabSyncResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sincronizar orden con LIS"
)
async def sync_order_to_lis(
    data: LabSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sincronizar una orden con el sistema LIS externo

    **Proceso:**
    1. Valida que la orden exista
    2. Valida que la orden esté en estado COMPLETADA o EN_PROCESO
    3. Crea un log de sincronización
    4. Envía los datos al LIS (cuando esté configurado)
    5. Registra el resultado de la sincronización

    **Campos:**
    - **order_id**: ID de la orden a sincronizar

    **Notas:**
    - Si la orden ya fue sincronizada exitosamente, retorna error
    - Si existe un log previo fallido, se reintenta automáticamente
    - Por ahora simula sincronización exitosa (integración real pendiente)
    """
    return await LabSyncService.sync_order_to_lis(db, data)


@router.post(
    "/{log_id}/retry",
    response_model=LabSyncResponse,
    summary="Reintentar sincronización fallida"
)
async def retry_sync(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Reintentar una sincronización que falló previamente

    **Proceso:**
    1. Valida que el log exista
    2. Valida que no sea una sincronización exitosa
    3. Incrementa el contador de intentos
    4. Reintenta la sincronización con el LIS

    **Restricción:** No se puede reintentar una sincronización exitosa
    """
    return await LabSyncService.retry_sync(db, log_id)

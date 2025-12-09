"""
Reconciliation Router (API endpoints for daily closures and reconciliation)
"""
from fastapi import APIRouter, Depends, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from src.core.database import get_db
from src.modules.reconciliation.service import ReconciliationService
from src.modules.reconciliation.schemas import (
    DailyClosureCreate, DailyClosureResponse, DailyClosureDetailResponse,
    DailyClosureListResponse, DailyClosureReopen,
    DiscrepancyResponse, DiscrepancyCreate, DiscrepancyResolve,
    ClosureStats, ReconciliationReport
)
from src.modules.reconciliation.models import ClosureStatus

router = APIRouter(prefix="/api/v1/reconciliation", tags=["Reconciliation"])


# ========================================
# DAILY CLOSURE ENDPOINTS
# ========================================

@router.get(
    "/closures",
    response_model=DailyClosureListResponse,
    summary="Listar cierres diarios - RF-062"
)
async def get_all_closures(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    location_id: Optional[int] = Query(None, description="Filtrar por sede"),
    status: Optional[ClosureStatus] = Query(None, description="Filtrar por estado"),
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener historial de cierres de caja diarios

    Permite consultar cierres anteriores con filtros:
    - Por sede
    - Por estado (OPEN, CLOSED)
    - Por rango de fechas
    """
    return await ReconciliationService.get_all_closures(
        db, page, page_size, location_id, status, date_from, date_to
    )


@router.get(
    "/closures/statistics",
    response_model=ClosureStats,
    summary="Obtener estadísticas de cierres"
)
async def get_closure_statistics(
    date_from: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas de cierres diarios

    - Total de cierres
    - Cierres abiertos/cerrados
    - Total de discrepancias
    - Discrepancias sin resolver
    """
    return await ReconciliationService.get_statistics(db, date_from, date_to)


@router.get(
    "/closures/{closure_id}",
    response_model=DailyClosureDetailResponse,
    summary="Obtener cierre por ID"
)
async def get_closure_by_id(
    closure_id: int = Path(..., gt=0, description="ID del cierre"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de un cierre incluyendo discrepancias
    """
    return await ReconciliationService.get_closure_by_id(db, closure_id)


@router.post(
    "/closures",
    response_model=DailyClosureDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cierre diario - RF-056, RF-057, RF-058"
)
async def create_daily_closure(
    data: DailyClosureCreate = Body(..., description="Datos del cierre"),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo cierre diario y ejecutar conciliación automática

    **Proceso:**
    1. Calcula el total esperado desde el sistema (órdenes + pagos)
    2. Compara con el total registrado manualmente
    3. Detecta discrepancias automáticamente (RF-058)
    4. Genera alertas si hay diferencias significativas (RF-061)

    **Validaciones:**
    - No permite duplicar cierres para la misma sede y fecha
    """
    return await ReconciliationService.create_daily_closure(db, data)


@router.put(
    "/closures/{closure_id}/close",
    response_model=DailyClosureResponse,
    summary="Cerrar cierre diario"
)
async def close_daily_closure(
    closure_id: int = Path(..., gt=0, description="ID del cierre"),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar un cierre diario (cambiar estado a CLOSED)

    Una vez cerrado, no se pueden agregar más discrepancias
    Solo el administrador puede reabrir un cierre cerrado
    """
    return await ReconciliationService.close_daily_closure(db, closure_id)


@router.post(
    "/closures/{closure_id}/reopen",
    response_model=DailyClosureResponse,
    summary="Reabrir cierre diario - RF-063"
)
async def reopen_closure(
    closure_id: int = Path(..., gt=0, description="ID del cierre"),
    data: DailyClosureReopen = Body(..., description="Justificación para reabrir"),
    db: AsyncSession = Depends(get_db)
):
    """
    Reabrir un cierre cerrado para realizar correcciones

    **Restricciones:**
    - Solo el administrador puede reabrir cierres
    - Requiere justificación (mínimo 10 caracteres)
    - Se registra en auditoría

    **Nota:** En producción, este endpoint debe tener autenticación
    y verificar que el usuario tenga rol de Administrador
    """
    return await ReconciliationService.reopen_closure(db, closure_id, data)


# ========================================
# DISCREPANCY ENDPOINTS
# ========================================

@router.post(
    "/closures/{closure_id}/discrepancies",
    response_model=DiscrepancyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar discrepancia manual"
)
async def add_discrepancy(
    closure_id: int = Path(..., gt=0, description="ID del cierre"),
    data: DiscrepancyCreate = Body(..., description="Datos de la discrepancia"),
    db: AsyncSession = Depends(get_db)
):
    """
    Agregar una discrepancia manual a un cierre

    Útil para registrar problemas identificados manualmente
    que no fueron detectados automáticamente
    """
    return await ReconciliationService.add_discrepancy(db, closure_id, data)


@router.put(
    "/discrepancies/{discrepancy_id}/resolve",
    response_model=DiscrepancyResponse,
    summary="Resolver discrepancia"
)
async def resolve_discrepancy(
    discrepancy_id: int = Path(..., gt=0, description="ID de la discrepancia"),
    data: DiscrepancyResolve = Body(..., description="Estado de resolución"),
    db: AsyncSession = Depends(get_db)
):
    """
    Marcar una discrepancia como resuelta

    Útil para hacer seguimiento de las correcciones realizadas
    """
    return await ReconciliationService.resolve_discrepancy(db, discrepancy_id, data)


# ========================================
# RECONCILIATION REPORT ENDPOINTS
# ========================================

@router.get(
    "/report",
    response_model=ReconciliationReport,
    summary="Generar reporte de conciliación - RF-057, RF-059"
)
async def get_reconciliation_report(
    location_id: int = Query(..., gt=0, description="ID de la sede"),
    closure_date: date = Query(..., description="Fecha del cierre (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generar reporte completo de conciliación

    **Incluye:**
    - Total de órdenes vs comprobantes (RF-057)
    - Total de pagos vs facturación
    - Resumen por método de pago (RF-059)
    - Discrepancias detectadas
    - Diferencias entre esperado y registrado

    **Uso:** Para cierre de caja diario y auditoría contable
    """
    return await ReconciliationService.get_reconciliation_report(
        db, location_id, closure_date
    )

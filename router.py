from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from src.core.database import get_db
from src.modules.orders import service as order_service
from src.modules.orders import schemas as order_schemas
# from src.core.security import require_roles

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
    # dependencies=[Depends(require_roles("Administrador General", "Supervisor de Sede"))]
)

@router.get("/orders-summary", response_model=order_schemas.OrderStats, summary="Obtener resumen de órdenes")
async def get_orders_summary(
    date_from: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Proporciona estadísticas clave sobre las órdenes de laboratorio en un rango de fechas.
    - **total_orders**: Número total de órdenes creadas.
    - **orders_by_status**: Desglose de órdenes por cada estado.
    - **total_revenue**: Suma de los montos finales de las órdenes completadas.
    - **Requiere rol:** Supervisor, Admin.
    """
    return await order_service.get_order_statistics(db, date_from, date_to)
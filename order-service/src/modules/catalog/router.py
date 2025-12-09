"""
Catalog Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal

from src.core.database import get_db
from src.modules.catalog.service import CategoryService, ServiceService
from src.modules.catalog.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithServicesCount,
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse,
    ServiceDetailResponse, UpdateServicePriceRequest, PriceHistoryListResponse
)

# Note: Authentication will be added later when integrating with user-service
# For now, endpoints are public for testing

# ==================== Category Router ====================

category_router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@category_router.get(
    "",
    response_model=List[CategoryResponse],
    summary="Listar todas las categorías"
)
async def get_all_categories(
    active_only: bool = Query(False, description="Solo categorías activas"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de todas las categorías

    **Filtros disponibles:**
    - **active_only**: Si es True, solo devuelve categorías activas
    """
    return await CategoryService.get_all_categories(db, active_only)


@category_router.get(
    "/with-count",
    response_model=List[CategoryWithServicesCount],
    summary="Listar categorías con contador de servicios"
)
async def get_all_categories_with_count(
    active_only: bool = Query(False, description="Solo categorías activas"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de categorías con el número de servicios en cada una

    **Filtros disponibles:**
    - **active_only**: Si es True, solo devuelve categorías activas
    """
    return await CategoryService.get_all_categories_with_count(db, active_only)


@category_router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Obtener categoría por ID"
)
async def get_category_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles de una categoría específica
    """
    return await CategoryService.get_category_by_id(db, category_id)


@category_router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva categoría"
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva categoría en el sistema

    - **name**: Nombre de la categoría (único, 1-100 caracteres)
    - **is_active**: Estado de la categoría (activo/inactivo, default: true)
    """
    return await CategoryService.create_category(db, data)


@category_router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Actualizar categoría"
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar una categoría existente

    **Nota:** Todos los campos son opcionales
    """
    return await CategoryService.update_category(db, category_id, data)


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar categoría"
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar una categoría del sistema

    **Nota:** No se puede eliminar una categoría que tenga servicios asociados
    """
    return await CategoryService.delete_category(db, category_id)


# ==================== Service Router ====================

service_router = APIRouter(prefix="/api/v1/services", tags=["Services"])


@service_router.get(
    "",
    response_model=ServiceListResponse,
    summary="Listar todos los servicios"
)
async def get_all_services(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    category_id: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Precio máximo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista paginada de servicios con filtros

    **Filtros disponibles:**
    - **search**: Busca en nombre y descripción del servicio
    - **category_id**: Filtra servicios de una categoría específica
    - **is_active**: Filtra por estado (true/false)
    - **min_price**: Precio mínimo
    - **max_price**: Precio máximo
    """
    return await ServiceService.get_all_services(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price
    )


@service_router.get(
    "/{service_id}",
    response_model=ServiceDetailResponse,
    summary="Obtener servicio por ID"
)
async def get_service_by_id(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de un servicio específico

    Incluye el historial de cambios de precio (últimos 10 cambios)
    """
    return await ServiceService.get_service_by_id(db, service_id)


@service_router.get(
    "/{service_id}/price-history",
    response_model=PriceHistoryListResponse,
    summary="Obtener historial de precios de un servicio"
)
async def get_price_history(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener el historial completo de cambios de precio para un servicio específico
    """
    return await ServiceService.get_price_history_by_service_id(db, service_id)


@service_router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo servicio"
)
async def create_service(
    data: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo servicio/examen en el sistema

    - **name**: Nombre del servicio (único, 1-255 caracteres)
    - **description**: Descripción del servicio (opcional)
    - **category_id**: ID de la categoría (debe existir)
    - **current_price**: Precio actual (debe ser > 0, máx. 2 decimales)
    - **is_active**: Estado del servicio (activo/inactivo, default: true)
    """
    return await ServiceService.create_service(db, data)


@service_router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Actualizar servicio"
)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información de un servicio

    **Nota:**
    - Todos los campos son opcionales
    - Para actualizar el precio, usar el endpoint específico PUT /{service_id}/price
    """
    return await ServiceService.update_service(db, service_id, data)


@service_router.put(
    "/{service_id}/price",
    response_model=ServiceResponse,
    summary="Actualizar precio de servicio"
)
async def update_service_price(
    service_id: int,
    data: UpdateServicePriceRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar el precio de un servicio

    Este endpoint actualiza el precio y automáticamente registra el cambio
    en el historial de precios.

    - **new_price**: Nuevo precio (debe ser > 0, máx. 2 decimales, diferente al actual)
    """
    return await ServiceService.update_service_price(db, service_id, data)


@service_router.delete(
    "/{service_id}",
    status_code=status.HTTP_200_OK,
    summary="Desactivar servicio"
)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Desactivar un servicio (soft delete)

    **Nota:** Esto marca al servicio como inactivo, no lo elimina físicamente
    """
    return await ServiceService.delete_service(db, service_id)

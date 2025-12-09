"""
Role Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.database import get_db
from src.core.security import get_current_user_id, require_roles
from src.services.role import RoleService
from src.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsersCount
from src.core.permissions import AVAILABLE_PERMISSIONS

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.get(
    "",
    response_model=List[RoleResponse],
    summary="Listar todos los roles",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def get_all_roles(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de todos los roles

    **Requiere rol:** Administrador General

    - **active_only**: Si es True, solo devuelve roles activos
    """
    return await RoleService.get_all_roles(db, active_only)


@router.get(
    "/with-count",
    response_model=List[RoleWithUsersCount],
    summary="Listar roles con contador de usuarios",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def get_all_roles_with_count(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de roles con el número de usuarios asignados a cada uno

    **Requiere rol:** Administrador General

    - **active_only**: Si es True, solo devuelve roles activos
    """
    return await RoleService.get_all_roles_with_count(db, active_only)


@router.get(
    "/available-permissions",
    summary="Listar todos los permisos disponibles",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def get_all_available_permissions():
    """
    Obtener una lista de todos los permisos disponibles en el sistema.
    """
    return AVAILABLE_PERMISSIONS


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Obtener rol por ID",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def get_role_by_id(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles de un rol específico

    **Requiere rol:** Administrador General
    """
    return await RoleService.get_role_by_id(db, role_id)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo rol",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo rol en el sistema

    **Requiere rol:** Administrador General

    - **name**: Nombre del rol (único)
    - **description**: Descripción del rol
    - **permissions**: Permisos en formato JSON
    - **is_active**: Estado del rol (activo/inactivo)
    """
    return await RoleService.create_role(db, data)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Actualizar rol",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un rol existente

    **Requiere rol:** Administrador General
    """
    return await RoleService.update_role(db, role_id, data)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar rol",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un rol del sistema

    **Requiere rol:** Administrador General

    **Nota:** No se puede eliminar un rol que tenga usuarios asignados
    """
    return await RoleService.delete_role(db, role_id)

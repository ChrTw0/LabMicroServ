"""
User Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.core.security import get_current_user_id, require_roles
from src.services.user import UserService
from src.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    UserListResponse, AssignRolesRequest, UpdateUserPasswordRequest
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar todos los usuarios",
    dependencies=[Depends(require_roles("Administrador General", "Supervisor de Sede"))]
)
async def get_all_users(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por email, nombre o apellido"),
    role_id: Optional[int] = Query(None, description="Filtrar por ID de rol"),
    location_id: Optional[int] = Query(None, description="Filtrar por ID de sede"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista paginada de usuarios con filtros

    **Requiere rol:** Administrador General o Supervisor de Sede

    **Filtros disponibles:**
    - **search**: Busca en email, nombre y apellido
    - **role_id**: Filtra usuarios con un rol específico
    - **location_id**: Filtra usuarios de una sede específica
    - **is_active**: Filtra por estado (true/false)
    """
    return await UserService.get_all_users(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        role_id=role_id,
        location_id=location_id,
        is_active=is_active
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Obtener usuario por ID",
    dependencies=[Depends(require_roles("Administrador General", "Supervisor de Sede"))]
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de un usuario específico

    **Requiere rol:** Administrador General o Supervisor de Sede
    """
    return await UserService.get_user_by_id(db, user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Crear un nuevo usuario en el sistema

    **Requiere rol:** Administrador General

    - **email**: Email del usuario (único)
    - **password**: Contraseña (mínimo 8 caracteres, mayúsculas y números)
    - **first_name**: Nombre
    - **last_name**: Apellido
    - **phone**: Teléfono (opcional)
    - **location_id**: ID de la sede (opcional)
    - **role_ids**: Lista de IDs de roles a asignar (mínimo 1)
    """
    return await UserService.create_user(db, data, current_user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Actualizar información de un usuario

    **Requiere rol:** Administrador General

    **Nota:** No se puede actualizar el email ni la contraseña desde este endpoint
    """
    return await UserService.update_user(db, user_id, data, current_user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Desactivar usuario",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Desactivar un usuario (soft delete)

    **Requiere rol:** Administrador General

    **Nota:** Esto marca al usuario como inactivo, no lo elimina físicamente
    """
    return await UserService.delete_user(db, user_id)


@router.put(
    "/{user_id}/roles",
    response_model=UserResponse,
    summary="Asignar roles a usuario",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def assign_roles_to_user(
    user_id: int,
    data: AssignRolesRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Asignar roles a un usuario (reemplaza los roles existentes)

    **Requiere rol:** Administrador General

    - **role_ids**: Lista de IDs de roles a asignar (mínimo 1)
    """
    return await UserService.assign_roles_to_user(db, user_id, data, current_user_id)


@router.put(
    "/{user_id}/password",
    status_code=status.HTTP_200_OK,
    summary="Actualizar contraseña de usuario (Admin)",
    dependencies=[Depends(require_roles("Administrador General"))]
)
async def update_user_password(
    user_id: int,
    data: UpdateUserPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar la contraseña de un usuario (solo administradores)

    **Requiere rol:** Administrador General

    **Nota:** Este endpoint permite a los administradores resetear contraseñas sin conocer la actual
    """
    return await UserService.update_user_password(db, user_id, data)

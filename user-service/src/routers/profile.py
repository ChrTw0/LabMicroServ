"""
Profile Router (API endpoints for user profile management - F-03)
RF-007: Gestión del perfil del usuario
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user_id
from src.services.user import UserService
from src.schemas.user import (
    ProfileResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest
)

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.get(
    "",
    response_model=ProfileResponse,
    summary="Ver mi perfil",
    description="Obtener información del perfil del usuario autenticado"
)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    **RF-007:** Ver mi perfil

    Permite a cualquier usuario autenticado consultar su propia información de perfil:
    - ID de usuario
    - Email
    - Nombre y apellido
    - Teléfono
    - Sede asignada
    - Roles asignados
    - Fechas de creación y actualización

    **Requiere:** Usuario autenticado (cualquier rol)
    """
    return await UserService.get_my_profile(db, current_user_id)


@router.put(
    "",
    response_model=ProfileResponse,
    summary="Actualizar mi perfil",
    description="Actualizar información básica del perfil (nombre, apellido, teléfono, email)"
)
async def update_my_profile(
    data: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    **RF-007:** Actualizar mi perfil

    Permite a cualquier usuario autenticado actualizar su información personal:
    - **first_name**: Nombre (opcional)
    - **last_name**: Apellido (opcional)
    - **phone**: Teléfono (opcional)
    - **email**: Email (opcional, debe ser único)

    **Validaciones:**
    - El email debe ser único en el sistema
    - Los datos se validan antes de guardar
    - Los cambios se confirman inmediatamente

    **Requiere:** Usuario autenticado (cualquier rol)
    """
    return await UserService.update_my_profile(db, current_user_id, data)


@router.put(
    "/password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar mi contraseña",
    description="Cambiar la contraseña del usuario autenticado"
)
async def change_my_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    **RF-007:** Cambiar mi contraseña

    Permite a cualquier usuario autenticado cambiar su propia contraseña.

    **Requisitos:**
    - **current_password**: Contraseña actual (para verificación)
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, con mayúsculas y números)

    **Validaciones:**
    - La contraseña actual debe ser correcta
    - La nueva contraseña debe cumplir con los requisitos de seguridad:
      - Mínimo 8 caracteres
      - Al menos una letra mayúscula
      - Al menos un número

    **Requiere:** Usuario autenticado (cualquier rol)
    """
    return await UserService.change_my_password(db, current_user_id, data)

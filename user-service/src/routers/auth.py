"""
Authentication Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user_id, get_current_user_payload
from src.services.auth import AuthService
from src.schemas.auth import (
    LoginRequest, LoginResponse, UserInfo,
    RegisterRequest, ChangePasswordRequest,
    RequestPasswordResetRequest, ResetPasswordRequest
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticar usuario y obtener token JWT

    - **email**: Email del usuario
    - **password**: Contraseña

    Retorna:
    - **access_token**: Token JWT para autenticación
    - **user**: Información del usuario autenticado
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await AuthService.login(db, data, ip_address, user_agent)


@router.post("/register", response_model=UserInfo, status_code=status.HTTP_201_CREATED, summary="Registrar nuevo usuario")
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Registrar un nuevo usuario en el sistema

    **Requiere autenticación**

    - **email**: Email del usuario (único)
    - **password**: Contraseña (mínimo 8 caracteres, debe incluir mayúsculas y números)
    - **first_name**: Nombre
    - **last_name**: Apellido
    - **phone**: Teléfono (opcional)
    - **location_id**: ID de la sede asignada (opcional)
    - **role_ids**: Lista de IDs de roles a asignar (mínimo 1)
    """
    return await AuthService.register(db, data, created_by=current_user_id)


@router.get("/me", response_model=UserInfo, summary="Obtener información del usuario actual")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Obtener información del usuario autenticado actualmente

    **Requiere autenticación**

    Retorna toda la información del perfil del usuario incluyendo roles asignados
    """
    return await AuthService.get_current_user_info(db, current_user_id)


@router.post("/change-password", summary="Cambiar contraseña")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Cambiar la contraseña del usuario autenticado

    **Requiere autenticación**

    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, debe incluir mayúsculas y números)
    """
    return await AuthService.change_password(db, current_user_id, data)


@router.post("/request-password-reset", summary="Solicitar restablecimiento de contraseña")
async def request_password_reset(
    data: RequestPasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Solicitar un token para restablecer contraseña

    **No requiere autenticación**

    - **email**: Email del usuario

    Por seguridad, siempre retorna un mensaje de éxito sin revelar si el email existe
    """
    return await AuthService.request_password_reset(db, data)


@router.post("/reset-password", summary="Restablecer contraseña con token")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Restablecer contraseña usando el token recibido por email

    **No requiere autenticación**

    - **token**: Token de recuperación recibido por email
    - **new_password**: Nueva contraseña (mínimo 8 caracteres, debe incluir mayúsculas y números)
    """
    return await AuthService.reset_password(db, data)


@router.post("/verify-token", summary="Verificar validez del token")
async def verify_token(
    payload: dict = Depends(get_current_user_payload)
):
    """
    Verificar si el token JWT es válido

    **Requiere autenticación**

    Retorna el payload del token si es válido
    """
    return {
        "valid": True,
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "roles": payload.get("roles", [])
    }

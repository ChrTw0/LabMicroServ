"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")


class UserInfo(BaseModel):
    """User information in token response"""
    id: int
    email: str
    first_name: str
    last_name: str
    roles: List[str] = Field(default_factory=list, description="Roles del usuario")
    permissions: List[str] = Field(default_factory=list, description="Permisos del usuario")
    location_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserInfo = Field(..., description="Información del usuario")


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    location_id: Optional[int] = Field(None, description="ID de la sede asignada")
    role_ids: List[int] = Field(..., min_items=1, description="IDs de los roles a asignar")

    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        return v


class RequestPasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr = Field(..., description="Email del usuario")


class ResetPasswordRequest(BaseModel):
    """Reset password with token"""
    token: str = Field(..., description="Token de recuperación")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        return v


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    user_id: int
    email: str
    roles: List[str]
    exp: datetime
    iat: datetime

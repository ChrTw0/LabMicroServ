"""
User Management Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="Email del usuario")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    location_id: Optional[int] = Field(None, description="ID de la sede asignada")
    is_active: bool = Field(default=True, description="Estado del usuario")


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, description="Contraseña")
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


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    location_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    roles: List[str] = Field(default_factory=list, description="Nombres de roles asignados")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response with additional info"""
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class UserListResponse(BaseModel):
    """Paginated list of users"""
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    users: List[UserResponse] = Field(..., description="Lista de usuarios")


class AssignRolesRequest(BaseModel):
    """Schema for assigning roles to a user"""
    role_ids: List[int] = Field(..., min_items=1, description="IDs de los roles a asignar")


class UpdateUserPasswordRequest(BaseModel):
    """Schema for admin updating user password"""
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


# ========== Profile Management Schemas (F-03) ==========

class ProfileUpdateRequest(BaseModel):
    """Schema for user updating their own profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    email: Optional[EmailStr] = Field(None, description="Email")


class ChangePasswordRequest(BaseModel):
    """Schema for user changing their own password"""
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


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    location_id: Optional[int] = None
    is_active: bool
    roles: List[str] = Field(default_factory=list, description="Nombres de roles asignados")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

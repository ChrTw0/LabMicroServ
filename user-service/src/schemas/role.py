"""
Role Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=50, description="Nombre del rol")
    description: Optional[str] = Field(None, max_length=255, description="Descripción del rol")
    permissions: Optional[str] = Field(None, description="Permisos en formato JSON")
    is_active: bool = Field(default=True, description="Estado del rol")


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoleWithUsersCount(RoleResponse):
    """Role with count of assigned users"""
    users_count: int = Field(default=0, description="Número de usuarios con este rol")

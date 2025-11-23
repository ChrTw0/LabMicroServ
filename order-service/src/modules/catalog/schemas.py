"""
Catalog Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    is_active: bool = Field(default=True, description="Estado de la categoría")


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int

    class Config:
        from_attributes = True


class CategoryWithServicesCount(CategoryResponse):
    """Category with count of services"""
    services_count: int = Field(default=0, description="Número de servicios en esta categoría")


# ==================== Service Schemas ====================

class ServiceBase(BaseModel):
    """Base service schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del servicio/examen")
    description: Optional[str] = Field(None, description="Descripción del servicio")
    category_id: int = Field(..., gt=0, description="ID de la categoría")
    current_price: Decimal = Field(..., gt=0, decimal_places=2, description="Precio actual")
    is_active: bool = Field(default=True, description="Estado del servicio")

    @validator('current_price')
    def validate_price(cls, v):
        """Validate price is positive and has max 2 decimal places"""
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        if v.as_tuple().exponent < -2:
            raise ValueError('El precio debe tener máximo 2 decimales')
        return v


class ServiceCreate(ServiceBase):
    """Schema for creating a service"""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class ServiceResponse(BaseModel):
    """Schema for service response"""
    id: int
    name: str
    description: Optional[str]
    category_id: int
    category_name: str = Field(..., description="Nombre de la categoría")
    current_price: Decimal
    is_active: bool

    class Config:
        from_attributes = True


# ==================== Price History Schemas ====================

class PriceHistoryResponse(BaseModel):
    """Schema for price history response"""
    id: int
    service_id: int
    old_price: Decimal
    new_price: Decimal
    changed_at: datetime

    class Config:
        from_attributes = True


# ==================== Price Update Schema ====================

class UpdateServicePriceRequest(BaseModel):
    """Schema for updating service price"""
    new_price: Decimal = Field(..., gt=0, decimal_places=2, description="Nuevo precio")

    @validator('new_price')
    def validate_price(cls, v):
        """Validate price is positive and has max 2 decimal places"""
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        if v.as_tuple().exponent < -2:
            raise ValueError('El precio debe tener máximo 2 decimales')
        return v


# ==================== Extended Service Schemas ====================

class ServiceDetailResponse(ServiceResponse):
    """Detailed service response with price history"""
    price_history: List[PriceHistoryResponse] = Field(default_factory=list)


class ServiceListResponse(BaseModel):
    """Paginated list of services"""
    total: int = Field(..., description="Total de servicios")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    services: List[ServiceResponse] = Field(..., description="Lista de servicios")


# ==================== Search/Filter Schemas ====================

class ServiceSearchFilters(BaseModel):
    """Filters for service search"""
    search: Optional[str] = Field(None, description="Buscar por nombre o descripción")
    category_id: Optional[int] = Field(None, description="Filtrar por categoría")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Precio mínimo")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Precio máximo")

"""
Configuration Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


# CompanyInfo Schemas
class CompanyInfoBase(BaseModel):
    ruc: str = Field(..., min_length=11, max_length=11, description="RUC de la empresa (11 dígitos)")
    business_name: str = Field(..., min_length=1, max_length=255, description="Razón social")
    address: str = Field(..., min_length=1, max_length=255, description="Dirección fiscal")

    @validator('ruc')
    def validate_ruc(cls, v):
        if not v.isdigit():
            raise ValueError('RUC debe contener solo dígitos')
        return v


class CompanyInfoCreate(CompanyInfoBase):
    pass


class CompanyInfoUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=255)


class CompanyInfoResponse(CompanyInfoBase):
    id: int

    class Config:
        from_attributes = True


# Location Schemas
class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la sede")
    is_active: bool = Field(default=True, description="Indica si la sede está activa")


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True


# SystemSetting Schemas
class SystemSettingBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=100, description="Clave del parámetro")
    value: str = Field(..., min_length=1, description="Valor del parámetro")


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    value: str = Field(..., min_length=1, description="Nuevo valor del parámetro")


class SystemSettingResponse(SystemSettingBase):
    id: int

    class Config:
        from_attributes = True


# Bulk settings update
class BulkSystemSettingsUpdate(BaseModel):
    settings: dict[str, str] = Field(..., description="Diccionario con key:value de configuraciones")

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


# ========== F-31: Parámetros fiscales y técnicos ==========

class SunatCredentialsRequest(BaseModel):
    """RF-086: Configurar credenciales SUNAT o PSE"""
    sol_user: str = Field(..., min_length=1, max_length=100, description="Usuario SOL o PSE")
    sol_password: str = Field(..., min_length=1, max_length=255, description="Contraseña SOL o PSE")
    certificate_path: Optional[str] = Field(None, max_length=255, description="Ruta del certificado digital")
    pse_url: Optional[str] = Field(None, max_length=255, description="URL del PSE (si aplica)")
    environment: str = Field(default="production", description="Ambiente: production o testing")

    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['production', 'testing']:
            raise ValueError('El ambiente debe ser "production" o "testing"')
        return v


class SmtpConfigRequest(BaseModel):
    """RF-087: Configurar servidor de correo SMTP"""
    smtp_host: str = Field(..., min_length=1, max_length=255, description="Servidor SMTP")
    smtp_port: int = Field(..., ge=1, le=65535, description="Puerto SMTP (generalmente 587 o 465)")
    smtp_user: str = Field(..., min_length=1, max_length=255, description="Usuario SMTP")
    smtp_password: str = Field(..., min_length=1, max_length=255, description="Contraseña SMTP")
    smtp_from_email: str = Field(..., min_length=1, max_length=255, description="Email remitente")
    smtp_from_name: str = Field(..., min_length=1, max_length=255, description="Nombre del remitente")
    use_tls: bool = Field(default=True, description="Usar TLS/SSL")

    @validator('smtp_port')
    def validate_smtp_port(cls, v):
        common_ports = [25, 465, 587, 2525]
        if v not in common_ports:
            raise ValueError(f'Puerto SMTP no común. Puertos típicos: {common_ports}')
        return v


class SunatCredentialsResponse(BaseModel):
    """Response for SUNAT credentials (sin exponer contraseñas)"""
    sol_user: str
    certificate_path: Optional[str]
    pse_url: Optional[str]
    environment: str
    configured: bool = True


class SmtpConfigResponse(BaseModel):
    """Response for SMTP config (sin exponer contraseñas)"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_from_email: str
    smtp_from_name: str
    use_tls: bool
    configured: bool = True

"""
Configuration Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.database import get_db
from src.modules.configuration.service import (
    CompanyInfoService,
    LocationService,
    SystemSettingService
)
from src.modules.configuration.schemas import (
    CompanyInfoCreate, CompanyInfoUpdate, CompanyInfoResponse,
    LocationCreate, LocationUpdate, LocationResponse,
    SystemSettingCreate, SystemSettingUpdate, SystemSettingResponse,
    BulkSystemSettingsUpdate
)

router = APIRouter(prefix="/api/v1/configuration", tags=["Configuration"])


# ==================== Company Info Endpoints ====================
@router.get("/company", response_model=CompanyInfoResponse, summary="Obtener información de la empresa")
async def get_company_info(db: AsyncSession = Depends(get_db)):
    """Obtiene la información de la empresa configurada en el sistema"""
    return await CompanyInfoService.get_company_info(db)


@router.post("/company", response_model=CompanyInfoResponse, status_code=status.HTTP_201_CREATED, summary="Crear información de la empresa")
async def create_company_info(data: CompanyInfoCreate, db: AsyncSession = Depends(get_db)):
    """Crea la información de la empresa (solo se permite una vez)"""
    return await CompanyInfoService.create_company_info(db, data)


@router.put("/company/{company_id}", response_model=CompanyInfoResponse, summary="Actualizar información de la empresa")
async def update_company_info(company_id: int, data: CompanyInfoUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza la información de la empresa"""
    return await CompanyInfoService.update_company_info(db, company_id, data)


# ==================== Location Endpoints ====================
@router.get("/locations", response_model=List[LocationResponse], summary="Listar todas las sedes")
async def get_all_locations(active_only: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Obtiene todas las sedes del sistema

    - **active_only**: Si es True, solo devuelve sedes activas
    """
    return await LocationService.get_all_locations(db, active_only)


@router.get("/locations/{location_id}", response_model=LocationResponse, summary="Obtener sede por ID")
async def get_location_by_id(location_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene los detalles de una sede específica"""
    return await LocationService.get_location_by_id(db, location_id)


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva sede")
async def create_location(data: LocationCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva sede en el sistema"""
    return await LocationService.create_location(db, data)


@router.put("/locations/{location_id}", response_model=LocationResponse, summary="Actualizar sede")
async def update_location(location_id: int, data: LocationUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza los datos de una sede existente"""
    return await LocationService.update_location(db, location_id, data)


@router.delete("/locations/{location_id}", status_code=status.HTTP_200_OK, summary="Eliminar sede")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina una sede del sistema"""
    return await LocationService.delete_location(db, location_id)


# ==================== System Settings Endpoints ====================
@router.get("/settings", response_model=List[SystemSettingResponse], summary="Listar todas las configuraciones")
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Obtiene todas las configuraciones del sistema"""
    return await SystemSettingService.get_all_settings(db)


@router.get("/settings/{key}", response_model=SystemSettingResponse, summary="Obtener configuración por clave")
async def get_setting_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """Obtiene una configuración específica por su clave"""
    return await SystemSettingService.get_setting_by_key(db, key)


@router.post("/settings", response_model=SystemSettingResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva configuración")
async def create_setting(data: SystemSettingCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva configuración en el sistema"""
    return await SystemSettingService.create_setting(db, data)


@router.put("/settings/{key}", response_model=SystemSettingResponse, summary="Actualizar configuración")
async def update_setting(key: str, data: SystemSettingUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza el valor de una configuración existente"""
    return await SystemSettingService.update_setting(db, key, data)


@router.put("/settings/{key}/upsert", response_model=SystemSettingResponse, summary="Crear o actualizar configuración")
async def upsert_setting(key: str, value: str, db: AsyncSession = Depends(get_db)):
    """Crea o actualiza una configuración (upsert)"""
    return await SystemSettingService.upsert_setting(db, key, value)


@router.post("/settings/bulk", response_model=List[SystemSettingResponse], summary="Actualizar múltiples configuraciones")
async def bulk_upsert_settings(data: BulkSystemSettingsUpdate, db: AsyncSession = Depends(get_db)):
    """Crea o actualiza múltiples configuraciones en una sola operación"""
    return await SystemSettingService.bulk_upsert_settings(db, data)


@router.delete("/settings/{key}", status_code=status.HTTP_200_OK, summary="Eliminar configuración")
async def delete_setting(key: str, db: AsyncSession = Depends(get_db)):
    """Elimina una configuración del sistema"""
    return await SystemSettingService.delete_setting(db, key)

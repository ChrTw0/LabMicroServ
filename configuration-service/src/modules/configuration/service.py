"""
Configuration Service (Business logic layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List, Optional

from src.modules.configuration.repository import (
    CompanyInfoRepository,
    LocationRepository,
    SystemSettingRepository
)
from src.modules.configuration.schemas import (
    CompanyInfoCreate, CompanyInfoUpdate, CompanyInfoResponse,
    LocationCreate, LocationUpdate, LocationResponse,
    SystemSettingCreate, SystemSettingUpdate, SystemSettingResponse,
    BulkSystemSettingsUpdate
)


class CompanyInfoService:
    """Service for CompanyInfo business logic"""

    @staticmethod
    async def get_company_info(db: AsyncSession) -> CompanyInfoResponse:
        """Get company information"""
        company = await CompanyInfoRepository.get(db)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Información de empresa no configurada"
            )
        return CompanyInfoResponse.model_validate(company)

    @staticmethod
    async def create_company_info(db: AsyncSession, data: CompanyInfoCreate) -> CompanyInfoResponse:
        """Create company information"""
        # Check if company info already exists
        existing = await CompanyInfoRepository.get(db)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La información de empresa ya está configurada. Use PUT para actualizar."
            )

        company = await CompanyInfoRepository.create(db, data)
        return CompanyInfoResponse.model_validate(company)

    @staticmethod
    async def update_company_info(db: AsyncSession, company_id: int, data: CompanyInfoUpdate) -> CompanyInfoResponse:
        """Update company information"""
        company = await CompanyInfoRepository.update(db, company_id, data)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Información de empresa no encontrada"
            )
        return CompanyInfoResponse.model_validate(company)


class LocationService:
    """Service for Location business logic"""

    @staticmethod
    async def get_all_locations(db: AsyncSession, active_only: bool = False) -> List[LocationResponse]:
        """Get all locations"""
        locations = await LocationRepository.get_all(db, active_only)
        return [LocationResponse.model_validate(loc) for loc in locations]

    @staticmethod
    async def get_location_by_id(db: AsyncSession, location_id: int) -> LocationResponse:
        """Get location by ID"""
        location = await LocationRepository.get_by_id(db, location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {location_id} no encontrada"
            )
        return LocationResponse.model_validate(location)

    @staticmethod
    async def create_location(db: AsyncSession, data: LocationCreate) -> LocationResponse:
        """Create a new location"""
        # Check if location with same name already exists
        existing = await LocationRepository.get_by_name(db, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una sede con el nombre '{data.name}'"
            )

        location = await LocationRepository.create(db, data)
        return LocationResponse.model_validate(location)

    @staticmethod
    async def update_location(db: AsyncSession, location_id: int, data: LocationUpdate) -> LocationResponse:
        """Update location"""
        # Check if location exists
        existing = await LocationRepository.get_by_id(db, location_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {location_id} no encontrada"
            )

        # If updating name, check for duplicates
        if data.name:
            name_exists = await LocationRepository.get_by_name(db, data.name)
            if name_exists and name_exists.id != location_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra sede con el nombre '{data.name}'"
                )

        location = await LocationRepository.update(db, location_id, data)
        return LocationResponse.model_validate(location)

    @staticmethod
    async def delete_location(db: AsyncSession, location_id: int) -> dict:
        """Delete location"""
        # Check if location exists
        existing = await LocationRepository.get_by_id(db, location_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {location_id} no encontrada"
            )

        deleted = await LocationRepository.delete(db, location_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la sede"
            )

        return {"message": f"Sede '{existing.name}' eliminada exitosamente"}


class SystemSettingService:
    """Service for SystemSetting business logic"""

    @staticmethod
    async def get_all_settings(db: AsyncSession) -> List[SystemSettingResponse]:
        """Get all system settings"""
        settings = await SystemSettingRepository.get_all(db)
        return [SystemSettingResponse.model_validate(s) for s in settings]

    @staticmethod
    async def get_setting_by_key(db: AsyncSession, key: str) -> SystemSettingResponse:
        """Get setting by key"""
        setting = await SystemSettingRepository.get_by_key(db, key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuración con clave '{key}' no encontrada"
            )
        return SystemSettingResponse.model_validate(setting)

    @staticmethod
    async def create_setting(db: AsyncSession, data: SystemSettingCreate) -> SystemSettingResponse:
        """Create a new system setting"""
        # Check if setting already exists
        existing = await SystemSettingRepository.get_by_key(db, data.key)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una configuración con la clave '{data.key}'"
            )

        setting = await SystemSettingRepository.create(db, data)
        return SystemSettingResponse.model_validate(setting)

    @staticmethod
    async def update_setting(db: AsyncSession, key: str, data: SystemSettingUpdate) -> SystemSettingResponse:
        """Update system setting"""
        setting = await SystemSettingRepository.update(db, key, data)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuración con clave '{key}' no encontrada"
            )
        return SystemSettingResponse.model_validate(setting)

    @staticmethod
    async def upsert_setting(db: AsyncSession, key: str, value: str) -> SystemSettingResponse:
        """Create or update a system setting"""
        setting = await SystemSettingRepository.upsert(db, key, value)
        return SystemSettingResponse.model_validate(setting)

    @staticmethod
    async def bulk_upsert_settings(db: AsyncSession, data: BulkSystemSettingsUpdate) -> List[SystemSettingResponse]:
        """Bulk create or update system settings"""
        results = []
        for key, value in data.settings.items():
            setting = await SystemSettingRepository.upsert(db, key, value)
            results.append(SystemSettingResponse.model_validate(setting))
        return results

    @staticmethod
    async def delete_setting(db: AsyncSession, key: str) -> dict:
        """Delete system setting"""
        # Check if setting exists
        existing = await SystemSettingRepository.get_by_key(db, key)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuración con clave '{key}' no encontrada"
            )

        deleted = await SystemSettingRepository.delete(db, key)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la configuración"
            )

        return {"message": f"Configuración '{key}' eliminada exitosamente"}

"""
Configuration Repository (Data access layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List

from src.modules.configuration.models import CompanyInfo, Location, SystemSetting
from src.modules.configuration.schemas import (
    CompanyInfoCreate, CompanyInfoUpdate,
    LocationCreate, LocationUpdate,
    SystemSettingCreate, SystemSettingUpdate
)


class CompanyInfoRepository:
    """Repository for CompanyInfo operations"""

    @staticmethod
    async def get(db: AsyncSession) -> Optional[CompanyInfo]:
        """Get company info (should be only one record)"""
        result = await db.execute(select(CompanyInfo))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: CompanyInfoCreate) -> CompanyInfo:
        """Create company info"""
        company = CompanyInfo(**data.model_dump())
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    @staticmethod
    async def update(db: AsyncSession, company_id: int, data: CompanyInfoUpdate) -> Optional[CompanyInfo]:
        """Update company info"""
        stmt = (
            update(CompanyInfo)
            .where(CompanyInfo.id == company_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(CompanyInfo)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()


class LocationRepository:
    """Repository for Location operations"""

    @staticmethod
    async def get_all(db: AsyncSession, active_only: bool = False) -> List[Location]:
        """Get all locations"""
        query = select(Location)
        if active_only:
            query = query.where(Location.is_active == True)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, location_id: int) -> Optional[Location]:
        """Get location by ID"""
        result = await db.execute(select(Location).where(Location.id == location_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Location]:
        """Get location by name"""
        result = await db.execute(select(Location).where(Location.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: LocationCreate) -> Location:
        """Create a new location"""
        location = Location(**data.model_dump())
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    @staticmethod
    async def update(db: AsyncSession, location_id: int, data: LocationUpdate) -> Optional[Location]:
        """Update location"""
        stmt = (
            update(Location)
            .where(Location.id == location_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Location)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, location_id: int) -> bool:
        """Delete location"""
        stmt = delete(Location).where(Location.id == location_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


class SystemSettingRepository:
    """Repository for SystemSetting operations"""

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SystemSetting]:
        """Get all system settings"""
        result = await db.execute(select(SystemSetting))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[SystemSetting]:
        """Get setting by key"""
        result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: SystemSettingCreate) -> SystemSetting:
        """Create a new system setting"""
        setting = SystemSetting(**data.model_dump())
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
        return setting

    @staticmethod
    async def update(db: AsyncSession, key: str, data: SystemSettingUpdate) -> Optional[SystemSetting]:
        """Update system setting by key"""
        stmt = (
            update(SystemSetting)
            .where(SystemSetting.key == key)
            .values(value=data.value)
            .returning(SystemSetting)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert(db: AsyncSession, key: str, value: str) -> SystemSetting:
        """Create or update a system setting"""
        existing = await SystemSettingRepository.get_by_key(db, key)
        if existing:
            return await SystemSettingRepository.update(db, key, SystemSettingUpdate(value=value))
        else:
            return await SystemSettingRepository.create(db, SystemSettingCreate(key=key, value=value))

    @staticmethod
    async def delete(db: AsyncSession, key: str) -> bool:
        """Delete system setting by key"""
        stmt = delete(SystemSetting).where(SystemSetting.key == key)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

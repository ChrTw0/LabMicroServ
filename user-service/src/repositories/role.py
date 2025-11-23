"""
Role Repository (Data access layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import Optional, List

from src.models.user import Role, UserRole
from src.schemas.role import RoleCreate, RoleUpdate


class RoleRepository:
    """Repository for Role operations"""

    @staticmethod
    async def get_all(db: AsyncSession, active_only: bool = False) -> List[Role]:
        """Get all roles"""
        query = select(Role)
        if active_only:
            query = query.where(Role.is_active == True)
        query = query.order_by(Role.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        result = await db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Role]:
        """Get role by name"""
        result = await db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_ids(db: AsyncSession, role_ids: List[int]) -> List[Role]:
        """Get multiple roles by IDs"""
        result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, data: RoleCreate) -> Role:
        """Create a new role"""
        role = Role(**data.model_dump())
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def update(db: AsyncSession, role_id: int, data: RoleUpdate) -> Optional[Role]:
        """Update role"""
        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Role)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, role_id: int) -> bool:
        """Delete role"""
        stmt = delete(Role).where(Role.id == role_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_users_count(db: AsyncSession, role_id: int) -> int:
        """Get count of users assigned to this role"""
        result = await db.execute(
            select(func.count(UserRole.id)).where(UserRole.role_id == role_id)
        )
        return result.scalar() or 0

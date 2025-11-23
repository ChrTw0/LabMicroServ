"""
User Repository (Data access layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from src.models.user import User, Role, UserRole
from src.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository for User operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role_id: Optional[int] = None,
        location_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """
        Get all users with pagination and filters

        Returns:
            Tuple of (users list, total count)
        """
        # Base query with roles loaded
        query = select(User).options(
            selectinload(User.user_roles).selectinload(UserRole.role)
        )

        # Apply filters
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        if role_id is not None:
            # Join with UserRole to filter by role
            query = query.join(User.user_roles).where(UserRole.role_id == role_id)

        if location_id is not None:
            query = query.where(User.location_id == location_id)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        users = list(result.unique().scalars().all())

        return users, total

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID with roles loaded"""
        stmt = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        location_id: Optional[int] = None,
        is_active: bool = True,
        created_by: Optional[int] = None
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            location_id=location_id,
            is_active=is_active,
            created_by=created_by
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(
        db: AsyncSession,
        user_id: int,
        data: UserUpdate,
        updated_by: Optional[int] = None
    ) -> Optional[User]:
        """Update user"""
        update_data = data.model_dump(exclude_unset=True)
        if updated_by:
            update_data['updated_by'] = updated_by

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False is preferred)"""
        stmt = delete(User).where(User.id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def update_password(
        db: AsyncSession,
        user_id: int,
        new_password_hash: str
    ) -> bool:
        """Update user password"""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=new_password_hash)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def assign_roles(
        db: AsyncSession,
        user_id: int,
        role_ids: List[int],
        assigned_by: Optional[int] = None
    ) -> List[UserRole]:
        """
        Assign roles to user (replaces existing roles)
        """
        # Remove existing roles
        await db.execute(delete(UserRole).where(UserRole.user_id == user_id))

        # Add new roles
        user_roles = []
        for role_id in role_ids:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by
            )
            db.add(user_role)
            user_roles.append(user_role)

        await db.commit()
        return user_roles

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
        """Get all roles assigned to a user"""
        stmt = (
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
            .where(Role.is_active == True)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

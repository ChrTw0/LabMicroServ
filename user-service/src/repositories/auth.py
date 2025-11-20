"""
Authentication Repository (Data access layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
import secrets

from src.models.user import User, Role, UserRole, PasswordResetToken, AuditLog


class AuthRepository:
    """Repository for authentication operations"""

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email with roles loaded

        Args:
            db: Database session
            email: User email

        Returns:
            User object with roles or None
        """
        stmt = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.email == email)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get user by ID with roles loaded

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object with roles or None
        """
        stmt = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        location_id: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> User:
        """
        Create a new user

        Args:
            db: Database session
            email: User email
            password_hash: Hashed password
            first_name: First name
            last_name: Last name
            phone: Phone number (optional)
            location_id: Location ID (optional)
            created_by: ID of user creating this user (optional)

        Returns:
            Created User object
        """
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            location_id=location_id,
            created_by=created_by
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def assign_roles_to_user(
        db: AsyncSession,
        user_id: int,
        role_ids: List[int],
        assigned_by: Optional[int] = None
    ) -> List[UserRole]:
        """
        Assign roles to a user

        Args:
            db: Database session
            user_id: User ID
            role_ids: List of role IDs to assign
            assigned_by: ID of user assigning roles (optional)

        Returns:
            List of created UserRole objects
        """
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
    async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        result = await db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_roles_by_ids(db: AsyncSession, role_ids: List[int]) -> List[Role]:
        """Get multiple roles by IDs"""
        result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
        return list(result.scalars().all())

    @staticmethod
    async def update_user_password(
        db: AsyncSession,
        user_id: int,
        new_password_hash: str
    ) -> bool:
        """
        Update user password

        Args:
            db: Database session
            user_id: User ID
            new_password_hash: New hashed password

        Returns:
            True if updated successfully
        """
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            return False

        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def create_password_reset_token(
        db: AsyncSession,
        user_id: int,
        expires_in_hours: int = 24
    ) -> PasswordResetToken:
        """
        Create a password reset token

        Args:
            db: Database session
            user_id: User ID
            expires_in_hours: Hours until token expires

        Returns:
            Created PasswordResetToken object
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(reset_token)
        await db.commit()
        await db.refresh(reset_token)
        return reset_token

    @staticmethod
    async def get_password_reset_token(
        db: AsyncSession,
        token: str
    ) -> Optional[PasswordResetToken]:
        """
        Get password reset token by token string

        Args:
            db: Database session
            token: Token string

        Returns:
            PasswordResetToken object or None
        """
        stmt = (
            select(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .where(PasswordResetToken.used_at.is_(None))
            .where(PasswordResetToken.expires_at > datetime.utcnow())
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def mark_token_as_used(
        db: AsyncSession,
        token_id: int
    ) -> bool:
        """
        Mark password reset token as used

        Args:
            db: Database session
            token_id: Token ID

        Returns:
            True if marked successfully
        """
        stmt = select(PasswordResetToken).where(PasswordResetToken.id == token_id)
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()

        if not token:
            return False

        token.used_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def create_audit_log(
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry

        Args:
            db: Database session
            user_id: User ID (optional for anonymous actions)
            action: Action performed (e.g., 'LOGIN', 'LOGOUT')
            entity_type: Type of entity affected (optional)
            entity_id: ID of entity affected (optional)
            ip_address: IP address (optional)
            user_agent: User agent string (optional)

        Returns:
            Created AuditLog object
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log

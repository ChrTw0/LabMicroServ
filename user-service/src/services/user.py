"""
User Service (Business logic layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from src.repositories.user import UserRepository
from src.repositories.role import RoleRepository
from src.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    UserListResponse, AssignRolesRequest, UpdateUserPasswordRequest
)
from src.core.security import hash_password


class UserService:
    """Service for user business logic"""

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        role_id: Optional[int] = None,
        location_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """Get all users with pagination and filters"""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50

        skip = (page - 1) * page_size

        users, total = await UserRepository.get_all(
            db=db,
            skip=skip,
            limit=page_size,
            search=search,
            role_id=role_id,
            location_id=location_id,
            is_active=is_active
        )

        # Convert to response schema
        user_responses = []
        for user in users:
            role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]
            user_dict = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'location_id': user.location_id,
                'is_active': user.is_active,
                'roles': role_names,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
            user_responses.append(UserResponse(**user_dict))

        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            users=user_responses
        )

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserDetailResponse:
        """Get user by ID"""
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]

        return UserDetailResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            location_id=user.location_id,
            is_active=user.is_active,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
            created_by=user.created_by,
            updated_by=user.updated_by
        )

    @staticmethod
    async def create_user(
        db: AsyncSession,
        data: UserCreate,
        created_by: int
    ) -> UserResponse:
        """Create a new user"""
        # Check if email already exists
        existing_user = await UserRepository.get_by_email(db, data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{data.email}' ya está registrado"
            )

        # Validate roles exist
        roles = await RoleRepository.get_by_ids(db, data.role_ids)
        if len(roles) != len(data.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más roles especificados no existen"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Create user
        user = await UserRepository.create(
            db=db,
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            location_id=data.location_id,
            is_active=True,
            created_by=created_by
        )

        # Assign roles
        await UserRepository.assign_roles(
            db=db,
            user_id=user.id,
            role_ids=data.role_ids,
            assigned_by=created_by
        )

        # Get user with roles
        user = await UserRepository.get_by_id(db, user.id)
        role_names = [ur.role.name for ur in user.user_roles]

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            location_id=user.location_id,
            is_active=user.is_active,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        data: UserUpdate,
        updated_by: int
    ) -> UserResponse:
        """Update user"""
        # Check if user exists
        existing = await UserRepository.get_by_id(db, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        # Update user
        user = await UserRepository.update(db, user_id, data, updated_by)

        # Get updated user with roles
        user = await UserRepository.get_by_id(db, user_id)
        role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            location_id=user.location_id,
            is_active=user.is_active,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> dict:
        """Delete user (soft delete preferred)"""
        # Check if user exists
        existing = await UserRepository.get_by_id(db, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        # Soft delete (deactivate)
        await UserRepository.update(
            db, user_id, UserUpdate(is_active=False)
        )

        return {"message": f"Usuario '{existing.email}' desactivado exitosamente"}

    @staticmethod
    async def assign_roles_to_user(
        db: AsyncSession,
        user_id: int,
        data: AssignRolesRequest,
        assigned_by: int
    ) -> UserResponse:
        """Assign roles to a user"""
        # Check if user exists
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        # Validate roles exist
        roles = await RoleRepository.get_by_ids(db, data.role_ids)
        if len(roles) != len(data.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más roles especificados no existen"
            )

        # Assign roles
        await UserRepository.assign_roles(db, user_id, data.role_ids, assigned_by)

        # Get user with updated roles
        user = await UserRepository.get_by_id(db, user_id)
        role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            location_id=user.location_id,
            is_active=user.is_active,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    async def update_user_password(
        db: AsyncSession,
        user_id: int,
        data: UpdateUserPasswordRequest
    ) -> dict:
        """Admin update user password"""
        # Check if user exists
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        await UserRepository.update_password(db, user_id, new_password_hash)

        return {"message": "Contraseña actualizada exitosamente"}

"""
Role Service (Business logic layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List

from src.repositories.role import RoleRepository
from src.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsersCount


class RoleService:
    """Service for role business logic"""

    @staticmethod
    async def get_all_roles(db: AsyncSession, active_only: bool = False) -> List[RoleResponse]:
        """Get all roles"""
        roles = await RoleRepository.get_all(db, active_only)
        return [RoleResponse.model_validate(role) for role in roles]

    @staticmethod
    async def get_all_roles_with_count(db: AsyncSession, active_only: bool = False) -> List[RoleWithUsersCount]:
        """Get all roles with user count"""
        roles = await RoleRepository.get_all(db, active_only)
        result = []
        for role in roles:
            users_count = await RoleRepository.get_users_count(db, role.id)
            role_dict = RoleResponse.model_validate(role).model_dump()
            role_dict['users_count'] = users_count
            result.append(RoleWithUsersCount(**role_dict))
        return result

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: int) -> RoleResponse:
        """Get role by ID"""
        role = await RoleRepository.get_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {role_id} no encontrado"
            )
        return RoleResponse.model_validate(role)

    @staticmethod
    async def create_role(db: AsyncSession, data: RoleCreate) -> RoleResponse:
        """Create a new role"""
        # Check if role with same name already exists
        existing = await RoleRepository.get_by_name(db, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un rol con el nombre '{data.name}'"
            )

        role = await RoleRepository.create(db, data)
        return RoleResponse.model_validate(role)

    @staticmethod
    async def update_role(db: AsyncSession, role_id: int, data: RoleUpdate) -> RoleResponse:
        """Update role"""
        # Check if role exists
        existing = await RoleRepository.get_by_id(db, role_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {role_id} no encontrado"
            )

        # If updating name, check for duplicates
        if data.name:
            name_exists = await RoleRepository.get_by_name(db, data.name)
            if name_exists and name_exists.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro rol con el nombre '{data.name}'"
                )

        role = await RoleRepository.update(db, role_id, data)
        return RoleResponse.model_validate(role)

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int) -> dict:
        """Delete role"""
        # Check if role exists
        existing = await RoleRepository.get_by_id(db, role_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {role_id} no encontrado"
            )

        # Check if role has users assigned
        users_count = await RoleRepository.get_users_count(db, role_id)
        if users_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el rol '{existing.name}' porque tiene {users_count} usuario(s) asignado(s)"
            )

        deleted = await RoleRepository.delete(db, role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el rol"
            )

        return {"message": f"Rol '{existing.name}' eliminado exitosamente"}

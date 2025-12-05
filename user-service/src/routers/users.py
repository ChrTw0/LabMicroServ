from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.database import get_db
from src.core.security import get_current_active_user, RoleChecker
from src.models.user import User as UserModel
from src.schemas import user as user_schema
from src.services import user as user_service

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
    dependencies=[Depends(get_current_active_user)]
)

admin_only = RoleChecker(["Administrador General"])

@router.get("/", response_model=List[user_schema.User], dependencies=[Depends(admin_only)])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Retrieve users.
    """
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_user(user: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create new user.
    """
    db_user = await user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=user_schema.User, dependencies=[Depends(admin_only)])
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get user by ID.
    """
    db_user = await user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=user_schema.User, dependencies=[Depends(admin_only)])
async def update_user(user_id: int, user: user_schema.UserUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a user.
    """
    db_user = await user_service.update_user(db=db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=user_schema.User, dependencies=[Depends(admin_only)])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a user.
    """
    db_user = await user_service.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/{user_id}/assign-role", response_model=user_schema.User, dependencies=[Depends(admin_only)])
async def assign_role_to_user(user_id: int, role_assign: user_schema.RoleAssign, db: AsyncSession = Depends(get_db)):
    """
    Assign a role to a user.
    """
    user = await user_service.assign_role(db, user_id=user_id, role_id=role_assign.role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or Role not found")
    return user

@router.post("/{user_id}/revoke-role", response_model=user_schema.User, dependencies=[Depends(admin_only)])
async def revoke_role_from_user(user_id: int, role_revoke: user_schema.RoleAssign, db: AsyncSession = Depends(get_db)):
    """
    Revoke a role from a user.
    """
    user = await user_service.revoke_role(db, user_id=user_id, role_id=role_revoke.role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or Role not found, or user does not have the role")
    return user

@router.get("/roles/", response_model=List[user_schema.Role], tags=["Roles"], dependencies=[Depends(admin_only)])
async def read_roles(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all roles.
    """
    return await user_service.get_roles(db)

@router.post("/roles/", response_model=user_schema.Role, tags=["Roles"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_role(role: user_schema.RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new role.
    """
    return await user_service.create_role(db, role)

@router.put("/roles/{role_id}", response_model=user_schema.Role, tags=["Roles"], dependencies=[Depends(admin_only)])
async def update_role(role_id: int, role: user_schema.RoleUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a role.
    """
    db_role = await user_service.update_role(db, role_id=role_id, role_update=role)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/roles/{role_id}", response_model=user_schema.Role, tags=["Roles"], dependencies=[Depends(admin_only)])
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a role.
    """
    db_role = await user_service.delete_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role
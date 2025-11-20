"""
Authentication Service (Business logic layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import timedelta

from src.repositories.auth import AuthRepository
from src.schemas.auth import (
    LoginRequest, LoginResponse, UserInfo,
    RegisterRequest, ChangePasswordRequest,
    RequestPasswordResetRequest, ResetPasswordRequest
)
from src.core.security import (
    verify_password, hash_password,
    create_access_token
)
from src.core.config import settings


class AuthService:
    """Service for authentication business logic"""

    @staticmethod
    async def login(db: AsyncSession, data: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> LoginResponse:
        """
        Authenticate user and return JWT token

        Args:
            db: Database session
            data: Login credentials
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            LoginResponse with access token and user info

        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await AuthRepository.get_user_by_email(db, data.email)

        if not user:
            # Create audit log for failed login attempt
            await AuthRepository.create_audit_log(
                db=db,
                user_id=None,
                action="LOGIN_FAILED",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        # Verify password
        if not verify_password(data.password, user.password_hash):
            # Create audit log for failed login attempt
            await AuthRepository.create_audit_log(
                db=db,
                user_id=user.id,
                action="LOGIN_FAILED",
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacte al administrador."
            )

        # Get user roles
        role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]

        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "roles": role_names
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )

        # Create audit log for successful login
        await AuthRepository.create_audit_log(
            db=db,
            user_id=user.id,
            action="LOGIN",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Prepare user info
        user_info = UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=role_names,
            location_id=user.location_id,
            is_active=user.is_active
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_info
        )

    @staticmethod
    async def register(
        db: AsyncSession,
        data: RegisterRequest,
        created_by: Optional[int] = None
    ) -> UserInfo:
        """
        Register a new user

        Args:
            db: Database session
            data: Registration data
            created_by: ID of user creating this user (optional)

        Returns:
            UserInfo of created user

        Raises:
            HTTPException: If email already exists or roles are invalid
        """
        # Check if email already exists
        existing_user = await AuthRepository.get_user_by_email(db, data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{data.email}' ya está registrado"
            )

        # Validate roles exist
        roles = await AuthRepository.get_roles_by_ids(db, data.role_ids)
        if len(roles) != len(data.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más roles especificados no existen"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Create user
        user = await AuthRepository.create_user(
            db=db,
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            location_id=data.location_id,
            created_by=created_by
        )

        # Assign roles
        await AuthRepository.assign_roles_to_user(
            db=db,
            user_id=user.id,
            role_ids=data.role_ids,
            assigned_by=created_by
        )

        # Create audit log
        await AuthRepository.create_audit_log(
            db=db,
            user_id=created_by,
            action="CREATE_USER",
            entity_type="User",
            entity_id=user.id
        )

        # Get user with roles
        user = await AuthRepository.get_user_by_id(db, user.id)
        role_names = [ur.role.name for ur in user.user_roles]

        return UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=role_names,
            location_id=user.location_id,
            is_active=user.is_active
        )

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        data: ChangePasswordRequest
    ) -> dict:
        """
        Change user password

        Args:
            db: Database session
            user_id: ID of user changing password
            data: Current and new passwords

        Returns:
            Success message

        Raises:
            HTTPException: If current password is incorrect
        """
        # Get user
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verify current password
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        await AuthRepository.update_user_password(db, user_id, new_password_hash)

        # Create audit log
        await AuthRepository.create_audit_log(
            db=db,
            user_id=user_id,
            action="CHANGE_PASSWORD"
        )

        return {"message": "Contraseña actualizada exitosamente"}

    @staticmethod
    async def request_password_reset(
        db: AsyncSession,
        data: RequestPasswordResetRequest
    ) -> dict:
        """
        Request password reset token

        Args:
            db: Database session
            data: Email to send reset token

        Returns:
            Success message (always returns success for security)
        """
        # Get user
        user = await AuthRepository.get_user_by_email(db, data.email)

        if user and user.is_active:
            # Create password reset token
            token_obj = await AuthRepository.create_password_reset_token(db, user.id)

            # TODO: Send email with token (integrate with notification service)
            # For now, just log it
            print(f"Password reset token for {user.email}: {token_obj.token}")

            # Create audit log
            await AuthRepository.create_audit_log(
                db=db,
                user_id=user.id,
                action="REQUEST_PASSWORD_RESET"
            )

        # Always return success for security (don't reveal if email exists)
        return {
            "message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña"
        }

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        data: ResetPasswordRequest
    ) -> dict:
        """
        Reset password using token

        Args:
            db: Database session
            data: Token and new password

        Returns:
            Success message

        Raises:
            HTTPException: If token is invalid or expired
        """
        # Get token
        token_obj = await AuthRepository.get_password_reset_token(db, data.token)

        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        await AuthRepository.update_user_password(db, token_obj.user_id, new_password_hash)

        # Mark token as used
        await AuthRepository.mark_token_as_used(db, token_obj.id)

        # Create audit log
        await AuthRepository.create_audit_log(
            db=db,
            user_id=token_obj.user_id,
            action="RESET_PASSWORD"
        )

        return {"message": "Contraseña restablecida exitosamente"}

    @staticmethod
    async def get_current_user_info(db: AsyncSession, user_id: int) -> UserInfo:
        """
        Get current user information

        Args:
            db: Database session
            user_id: User ID from JWT token

        Returns:
            UserInfo

        Raises:
            HTTPException: If user not found
        """
        user = await AuthRepository.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        role_names = [ur.role.name for ur in user.user_roles if ur.role.is_active]

        return UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=role_names,
            location_id=user.location_id,
            is_active=user.is_active
        )

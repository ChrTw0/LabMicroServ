"""
Seed script to populate initial data for user-service

This script creates:
- Default roles (Administrador General, Recepcionista, Supervisor de Sede, Laboratorista)
- Admin user (admin@labclinico.com)
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from loguru import logger

from src.core.config import settings
from src.core.security import hash_password
from src.models.user import User, Role, UserRole

# Configure logger
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)


async def create_roles(session: AsyncSession) -> dict[str, Role]:
    """Create default roles"""
    logger.info("Creating default roles...")

    roles_data = [
        {
            "name": "Administrador General",
            "description": "Acceso completo al sistema, gestión de usuarios, configuraciones y permisos",
            "permissions": '["all"]'
        },
        {
            "name": "Recepcionista",
            "description": "Registro de pacientes, creación de órdenes, gestión de pagos",
            "permissions": '["patients:read", "patients:write", "orders:read", "orders:write", "billing:read", "billing:write"]'
        },
        {
            "name": "Supervisor de Sede",
            "description": "Supervisión de operaciones, reportes, conciliación diaria",
            "permissions": '["patients:read", "orders:read", "billing:read", "reports:read", "reconciliation:read", "reconciliation:write"]'
        },
        {
            "name": "Laboratorista",
            "description": "Gestión de resultados de laboratorio, integración con LIS",
            "permissions": '["orders:read", "lab:read", "lab:write"]'
        }
    ]

    created_roles = {}

    for role_data in roles_data:
        # Check if role already exists
        result = await session.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        existing_role = result.scalar_one_or_none()

        if existing_role:
            logger.info(f"Role '{role_data['name']}' already exists, skipping...")
            created_roles[role_data["name"]] = existing_role
        else:
            role = Role(**role_data)
            session.add(role)
            await session.flush()
            await session.refresh(role)
            created_roles[role_data["name"]] = role
            logger.success(f"Created role: {role_data['name']} (ID: {role.id})")

    await session.commit()
    return created_roles


async def create_admin_user(session: AsyncSession, roles: dict[str, Role]) -> User:
    """Create admin user"""
    logger.info("Creating admin user...")

    admin_email = "admin@labclinico.com"
    admin_password = "Admin123"  # Change this in production!

    # Check if admin already exists
    result = await session.execute(
        select(User).where(User.email == admin_email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Admin user '{admin_email}' already exists, skipping...")
        return existing_user

    # Create admin user
    password_hash = hash_password(admin_password)

    admin_user = User(
        email=admin_email,
        password_hash=password_hash,
        first_name="Admin",
        last_name="Sistema",
        phone="+51999999999",
        is_active=True
    )

    session.add(admin_user)
    await session.flush()
    await session.refresh(admin_user)

    # Assign Administrador General role
    admin_role = roles["Administrador General"]
    user_role = UserRole(
        user_id=admin_user.id,
        role_id=admin_role.id
    )
    session.add(user_role)

    await session.commit()

    logger.success(f"Created admin user: {admin_email} (ID: {admin_user.id})")
    logger.info(f"  Password: {admin_password}")
    logger.warning("  ⚠️  IMPORTANT: Change the admin password after first login!")

    return admin_user


async def seed_database():
    """Main seed function"""
    logger.info("=" * 60)
    logger.info("Starting database seeding for user-service")
    logger.info("=" * 60)

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False
    )

    # Create async session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Create roles
            roles = await create_roles(session)

            # Create admin user
            admin_user = await create_admin_user(session, roles)

            logger.info("=" * 60)
            logger.success("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📋 Summary:")
            logger.info(f"  - Roles created: {len(roles)}")
            logger.info(f"  - Admin user: admin@labclinico.com")
            logger.info(f"  - Admin password: Admin123")
            logger.info("")
            logger.info("🔐 You can now login with these credentials:")
            logger.info("  POST http://localhost:8001/api/v1/auth/login")
            logger.info('  Body: {"email": "admin@labclinico.com", "password": "Admin123"}')
            logger.info("")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())

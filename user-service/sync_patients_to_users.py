"""
Synchronize existing patients to the user database.

This script connects to both the patient and user databases, finds patients
that do not have a corresponding user account, and creates a user for them.
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, table, column, String, Boolean, Integer
from loguru import logger
import sys
from pathlib import Path

# The execution environment (e.g., Docker container) should have the correct PYTHONPATH.
# For local execution, ensure the root of the project is in your PYTHONPATH.
sys.path.insert(0, '/app')

from src.models.user import User, Role, UserRole
from src.core.security import hash_password

# --- Configuration ---
# Use environment variables, with fallbacks for local execution
PATIENT_DB_URL = os.getenv("PATIENT_DB_URL", "postgresql+asyncpg://postgres:1234@patient-db:5432/patient_db")
USER_DB_URL = os.getenv("USER_DB_URL", "postgresql+asyncpg://postgres:1234@user-db:5432/user_db")
PATIENT_ROLE_ID = int(os.getenv("PATIENT_ROLE_ID", 6))

# Logger setup
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

# Lightweight table definition for patients
patients_table = table(
    "patients",
    column("id", Integer),
    column("email", String),
    column("document_number", String),
    column("first_name", String),
    column("last_name", String),
    column("phone", String),
    column("is_active", Boolean),
)

async def get_db_session(db_url: str):
    """Creates and returns an async session for the given database URL."""
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


async def main():
    logger.info("Starting synchronization of patients to users...")

    patient_session = await get_db_session(PATIENT_DB_URL)
    user_session = await get_db_session(USER_DB_URL)

    try:
        # 1. Get all patients with an email
        stmt = select(patients_table).where(patients_table.c.email.isnot(None))
        result = await patient_session.execute(stmt)
        all_patients = result.fetchall()
        logger.info(f"Found {len(all_patients)} patients with an email in the patient database.")

        # 2. Get all existing user emails
        stmt_users = select(User.email)
        result_users = await user_session.execute(stmt_users)
        existing_user_emails = {email for email, in result_users}
        logger.info(f"Found {len(existing_user_emails)} existing users in the user database.")

        # 3. Find patients without a user and create them
        users_to_create = []
        emails_to_create = set()
        for patient in all_patients:
            if patient.email not in existing_user_emails and patient.email not in emails_to_create:
                logger.warning(f"Patient with email '{patient.email}' does not have a user. Preparing to create one.")
                
                # Use document number as a temporary password
                password_hash = hash_password(f"P{patient.document_number}!")
                
                new_user = User(
                    email=patient.email,
                    password_hash=password_hash,
                    first_name=patient.first_name or "Usuario",
                    last_name=patient.last_name or "Paciente",
                    phone=patient.phone,
                    is_active=True,
                )
                users_to_create.append(new_user)
                emails_to_create.add(patient.email)

        if not users_to_create:
            logger.success("All patients with emails already have a corresponding user. No action needed.")
            return

        # 4. Create the new users
        logger.info(f"Creating {len(users_to_create)} new users...")
        user_session.add_all(users_to_create)
        await user_session.flush()

        # 5. Assign the "Paciente" role to the new users
        for user in users_to_create:
            await user_session.refresh(user) # Get the new user ID
            user_role = UserRole(
                user_id=user.id,
                role_id=PATIENT_ROLE_ID,
            )
            user_session.add(user_role)
            logger.success(f"User created and role 'Paciente' assigned for email '{user.email}' (User ID: {user.id})")

        await user_session.commit()
        logger.success(f"Successfully synchronized {len(users_to_create)} patients.")

    except Exception as e:
        logger.error(f"An error occurred during synchronization: {e}")
        await user_session.rollback()
    finally:
        await patient_session.close()
        await user_session.close()

if __name__ == "__main__":
    asyncio.run(main())
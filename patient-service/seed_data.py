"""
Seed script to populate initial data for patient-service

This script creates:
- Sample patients (both DNI and RUC)
- Sample notes for some patients
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
from src.models.patient import Patient, PatientNote, DocumentType

# Configure logger
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)


async def create_patients(session: AsyncSession) -> list[Patient]:
    """Create sample patients"""
    logger.info("Creating sample patients...")

    patients_data = [
        # Pacientes con DNI
        {
            "document_type": DocumentType.DNI,
            "document_number": "12345678",
            "first_name": "Juan",
            "last_name": "Pérez García",
            "phone": "+51987654321",
            "email": "juan.perez@email.com",
            "address": "Av. Los Álamos 123, Lima",
            "is_recurrent": False,
            "visit_count": 1
        },
        {
            "document_type": DocumentType.DNI,
            "document_number": "87654321",
            "first_name": "María",
            "last_name": "González López",
            "phone": "+51998765432",
            "email": "maria.gonzalez@email.com",
            "address": "Jr. Las Flores 456, Lima",
            "is_recurrent": True,
            "visit_count": 5
        },
        {
            "document_type": DocumentType.DNI,
            "document_number": "45678912",
            "first_name": "Carlos",
            "last_name": "Rodríguez Sánchez",
            "phone": "+51912345678",
            "email": "carlos.rodriguez@email.com",
            "address": "Calle Los Pinos 789, Miraflores",
            "is_recurrent": True,
            "visit_count": 8
        },
        {
            "document_type": DocumentType.DNI,
            "document_number": "78912345",
            "first_name": "Ana",
            "last_name": "Martínez Torres",
            "phone": "+51923456789",
            "email": "ana.martinez@email.com",
            "address": "Av. Larco 321, San Isidro",
            "is_recurrent": False,
            "visit_count": 2
        },
        {
            "document_type": DocumentType.DNI,
            "document_number": "65432198",
            "first_name": "Luis",
            "last_name": "Fernández Ramos",
            "phone": "+51934567890",
            "email": None,
            "address": None,
            "is_recurrent": False,
            "visit_count": 1
        },
        # Pacientes con RUC (empresas)
        {
            "document_type": DocumentType.RUC,
            "document_number": "20123456789",
            "first_name": None,
            "last_name": None,
            "business_name": "Laboratorios Médicos S.A.C.",
            "phone": "+5114567890",
            "email": "contacto@labmedicos.com",
            "address": "Av. Javier Prado 1234, San Isidro",
            "is_recurrent": True,
            "visit_count": 12
        },
        {
            "document_type": DocumentType.RUC,
            "document_number": "20987654321",
            "first_name": None,
            "last_name": None,
            "business_name": "Clínica Santa Rosa E.I.R.L.",
            "phone": "+5114567891",
            "email": "info@clinicasantarosa.com",
            "address": "Jr. Washington 567, Lima",
            "is_recurrent": True,
            "visit_count": 6
        },
        {
            "document_type": DocumentType.RUC,
            "document_number": "20456789123",
            "first_name": None,
            "last_name": None,
            "business_name": "Hospital Central del Perú S.A.",
            "phone": "+5114567892",
            "email": "contacto@hospitalcentral.pe",
            "address": "Av. Venezuela 890, Cercado de Lima",
            "is_recurrent": False,
            "visit_count": 2
        },
    ]

    created_patients = []

    for patient_data in patients_data:
        # Check if patient already exists
        result = await session.execute(
            select(Patient).where(Patient.document_number == patient_data["document_number"])
        )
        existing_patient = result.scalar_one_or_none()

        if existing_patient:
            logger.info(f"Patient '{patient_data['document_number']}' already exists, skipping...")
            created_patients.append(existing_patient)
        else:
            patient = Patient(**patient_data)
            session.add(patient)
            await session.flush()
            await session.refresh(patient)
            created_patients.append(patient)

            if patient.document_type == DocumentType.DNI:
                name = f"{patient.first_name} {patient.last_name}"
            else:
                name = patient.business_name

            logger.success(f"Created patient: {name} ({patient.document_number})")

    await session.commit()
    return created_patients


async def create_notes(session: AsyncSession, patients: list[Patient]) -> int:
    """Create sample notes for patients"""
    logger.info("Creating sample notes...")

    notes_data = [
        # Notas para Juan Pérez (paciente 1)
        {"patient_idx": 0, "note": "Paciente presenta alergia a la penicilina. Importante tener en cuenta para futuros tratamientos."},

        # Notas para María González (paciente 2)
        {"patient_idx": 1, "note": "Paciente recurrente. Realiza chequeos mensuales de glucosa."},
        {"patient_idx": 1, "note": "Recordar que prefiere atención en horario de tarde."},

        # Notas para Carlos Rodríguez (paciente 3)
        {"patient_idx": 2, "note": "Paciente con historial de hipertensión. Monitoreo constante requerido."},
        {"patient_idx": 2, "note": "Paciente muy puntual, siempre llega 10 minutos antes."},
        {"patient_idx": 2, "note": "Solicita copia de resultados en físico además del digital."},

        # Notas para Laboratorios Médicos S.A.C. (paciente 6)
        {"patient_idx": 5, "note": "Cliente corporativo. Facturación mensual consolidada."},
        {"patient_idx": 5, "note": "Descuento del 15% aplicado según contrato vigente."},
    ]

    created_count = 0

    for note_data in notes_data:
        patient = patients[note_data["patient_idx"]]

        note = PatientNote(
            patient_id=patient.id,
            note=note_data["note"],
            created_by=1  # Assuming admin user ID
        )
        session.add(note)
        created_count += 1
        logger.success(f"Created note for patient ID {patient.id}")

    await session.commit()
    return created_count


async def seed_database():
    """Main seed function"""
    logger.info("=" * 60)
    logger.info("Starting database seeding for patient-service")
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
            # Create patients
            patients = await create_patients(session)

            # Create notes
            notes_count = await create_notes(session, patients)

            logger.info("=" * 60)
            logger.success("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📋 Summary:")
            logger.info(f"  - Patients created: {len(patients)}")
            logger.info(f"  - Notes created: {notes_count}")
            logger.info("")
            logger.info("🔍 You can now explore the patients:")
            logger.info("  Patients: GET http://localhost:8002/api/v1/patients")
            logger.info("  By document: GET http://localhost:8002/api/v1/patients/document/12345678")
            logger.info("  API Docs: http://localhost:8002/docs")
            logger.info("")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())

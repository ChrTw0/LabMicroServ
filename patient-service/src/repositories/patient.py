"""
Patient Repository (Database operations)
"""
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from src.models.patient import Patient, PatientNote, PatientHistory, DocumentType


class PatientRepository:
    """Repository for Patient operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        is_recurrent: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Patient], int]:
        """Get all patients with filters and pagination"""
        query = select(Patient)

        # Apply filters
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Patient.document_number.ilike(search_pattern),
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                    Patient.business_name.ilike(search_pattern),
                    Patient.email.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern)
                )
            )
        if document_type is not None:
            filters.append(Patient.document_type == document_type)
        if is_recurrent is not None:
            filters.append(Patient.is_recurrent == is_recurrent)
        if is_active is not None:
            filters.append(Patient.is_active == is_active)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Patient)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Patient.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        patients = list(result.scalars().all())

        return patients, total

    @staticmethod
    async def get_by_id(db: AsyncSession, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        query = select(Patient).where(Patient.id == patient_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_notes(db: AsyncSession, patient_id: int) -> Optional[Patient]:
        """Get patient by ID with notes"""
        query = (
            select(Patient)
            .options(selectinload(Patient.notes))
            .where(Patient.id == patient_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_document(db: AsyncSession, document_number: str) -> Optional[Patient]:
        """Get patient by document number"""
        query = select(Patient).where(Patient.document_number == document_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, patient: Patient) -> Patient:
        """Create a new patient"""
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def update(db: AsyncSession, patient: Patient) -> Patient:
        """Update patient"""
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def delete(db: AsyncSession, patient: Patient) -> None:
        """Delete patient (soft delete by setting is_active=False)"""
        patient.is_active = False
        await db.commit()

    @staticmethod
    async def increment_visit_count(db: AsyncSession, patient_id: int) -> None:
        """Increment patient visit count"""
        patient = await PatientRepository.get_by_id(db, patient_id)
        if patient:
            patient.visit_count += 1
            if patient.visit_count >= 3:
                patient.is_recurrent = True
            await db.commit()


class PatientNoteRepository:
    """Repository for PatientNote operations"""

    @staticmethod
    async def get_by_patient_id(
        db: AsyncSession,
        patient_id: int,
        limit: int = 10
    ) -> List[PatientNote]:
        """Get notes for a patient"""
        query = (
            select(PatientNote)
            .where(PatientNote.patient_id == patient_id)
            .order_by(PatientNote.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, note: PatientNote) -> PatientNote:
        """Create a new note"""
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note

    @staticmethod
    async def delete(db: AsyncSession, note: PatientNote) -> None:
        """Delete note"""
        await db.delete(note)
        await db.commit()


class PatientHistoryRepository:
    """Repository for PatientHistory operations"""

    @staticmethod
    async def get_by_patient_id(
        db: AsyncSession,
        patient_id: int,
        limit: int = 20
    ) -> List[PatientHistory]:
        """Get history for a patient"""
        query = (
            select(PatientHistory)
            .where(PatientHistory.patient_id == patient_id)
            .order_by(PatientHistory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, history: PatientHistory) -> PatientHistory:
        """Create a new history record"""
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

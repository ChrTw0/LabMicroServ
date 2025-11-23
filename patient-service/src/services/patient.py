"""
Patient Service (Business logic)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List, Dict

from src.models.patient import Patient, PatientNote, PatientHistory, DocumentType
from src.repositories.patient import PatientRepository, PatientNoteRepository, PatientHistoryRepository
from src.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientDetailResponse,
    PatientListResponse, PatientNoteCreate, PatientNoteResponse
)


class PatientService:
    """Business logic for Patient operations"""

    @staticmethod
    async def get_all_patients(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        is_recurrent: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> PatientListResponse:
        """Get all patients with filters and pagination"""
        patients, total = await PatientRepository.get_all(
            db, page, page_size, search, document_type, is_recurrent, is_active
        )

        patient_responses = [PatientResponse.model_validate(p) for p in patients]

        return PatientListResponse(
            total=total,
            page=page,
            page_size=page_size,
            patients=patient_responses
        )

    @staticmethod
    async def get_patient_by_id(db: AsyncSession, patient_id: int) -> PatientDetailResponse:
        """Get patient by ID with notes"""
        patient = await PatientRepository.get_by_id_with_notes(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        # Convert to response with notes
        patient_dict = {
            "id": patient.id,
            "document_type": patient.document_type,
            "document_number": patient.document_number,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "business_name": patient.business_name,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "is_recurrent": patient.is_recurrent,
            "visit_count": patient.visit_count,
            "is_active": patient.is_active,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at,
            "notes": [PatientNoteResponse.model_validate(note) for note in patient.notes]
        }
        return PatientDetailResponse(**patient_dict)

    @staticmethod
    async def get_patient_by_document(db: AsyncSession, document_number: str) -> PatientResponse:
        """Get patient by document number"""
        patient = await PatientRepository.get_by_document(db, document_number)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con documento {document_number} no encontrado"
            )
        return PatientResponse.model_validate(patient)

    @staticmethod
    async def create_patient(
        db: AsyncSession,
        data: PatientCreate,
        created_by: Optional[int] = None
    ) -> PatientResponse:
        """Create a new patient"""
        # Check if patient with document already exists
        existing = await PatientRepository.get_by_document(db, data.document_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un paciente con el documento {data.document_number}"
            )

        # Create patient
        patient = Patient(
            document_type=data.document_type,
            document_number=data.document_number,
            first_name=data.first_name,
            last_name=data.last_name,
            business_name=data.business_name,
            phone=data.phone,
            email=data.email,
            address=data.address,
            created_by=created_by
        )
        patient = await PatientRepository.create(db, patient)
        return PatientResponse.model_validate(patient)

    @staticmethod
    async def update_patient(
        db: AsyncSession,
        patient_id: int,
        data: PatientUpdate,
        updated_by: Optional[int] = None
    ) -> PatientResponse:
        """Update patient"""
        patient = await PatientRepository.get_by_id(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        # Update fields
        if data.phone is not None:
            patient.phone = data.phone
        if data.email is not None:
            patient.email = data.email
        if data.address is not None:
            patient.address = data.address
        if data.is_active is not None:
            patient.is_active = data.is_active

        patient.updated_by = updated_by
        patient = await PatientRepository.update(db, patient)
        return PatientResponse.model_validate(patient)

    @staticmethod
    async def delete_patient(db: AsyncSession, patient_id: int) -> Dict[str, str]:
        """Delete patient (soft delete)"""
        patient = await PatientRepository.get_by_id(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        name = patient.business_name if patient.document_type == DocumentType.RUC else f"{patient.first_name} {patient.last_name}"
        await PatientRepository.delete(db, patient)
        return {"message": f"Paciente '{name}' desactivado exitosamente"}

    @staticmethod
    async def add_note_to_patient(
        db: AsyncSession,
        patient_id: int,
        data: PatientNoteCreate,
        created_by: Optional[int] = None
    ) -> PatientNoteResponse:
        """Add a note to a patient"""
        patient = await PatientRepository.get_by_id(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        note = PatientNote(
            patient_id=patient_id,
            note=data.note,
            created_by=created_by
        )
        note = await PatientNoteRepository.create(db, note)
        return PatientNoteResponse.model_validate(note)

    @staticmethod
    async def get_patient_notes(
        db: AsyncSession,
        patient_id: int,
        limit: int = 10
    ) -> List[PatientNoteResponse]:
        """Get notes for a patient"""
        patient = await PatientRepository.get_by_id(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {patient_id} no encontrado"
            )

        notes = await PatientNoteRepository.get_by_patient_id(db, patient_id, limit)
        return [PatientNoteResponse.model_validate(note) for note in notes]

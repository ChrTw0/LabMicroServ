"""
Patient Router (API endpoints)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.core.database import get_db
from src.services.patient import PatientService
from src.schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientDetailResponse,
    PatientListResponse, PatientNoteCreate, PatientNoteResponse
)
from src.models.patient import DocumentType

# Note: Authentication will be added later when integrating with user-service
# For now, endpoints are public for testing

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])


@router.get(
    "",
    response_model=PatientListResponse,
    summary="Listar todos los pacientes"
)
async def get_all_patients(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por documento, nombre, email o teléfono"),
    document_type: Optional[DocumentType] = Query(None, description="Filtrar por tipo de documento"),
    is_recurrent: Optional[bool] = Query(None, description="Filtrar por pacientes recurrentes"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista paginada de pacientes con filtros

    **Filtros disponibles:**
    - **search**: Busca en documento, nombres, apellidos, razón social, email y teléfono
    - **document_type**: Filtra por DNI o RUC
    - **is_recurrent**: Filtra pacientes recurrentes (3+ visitas)
    - **is_active**: Filtra por estado (true/false)
    """
    return await PatientService.get_all_patients(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        document_type=document_type,
        is_recurrent=is_recurrent,
        is_active=is_active
    )


@router.get(
    "/document/{document_number}",
    response_model=PatientResponse,
    summary="Buscar paciente por documento"
)
async def get_patient_by_document(
    document_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar paciente por número de documento (DNI o RUC)

    Útil para verificar si un paciente ya existe antes de crear uno nuevo
    """
    return await PatientService.get_patient_by_document(db, document_number)


@router.get(
    "/{patient_id}",
    response_model=PatientDetailResponse,
    summary="Obtener paciente por ID"
)
async def get_patient_by_id(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles completos de un paciente específico

    Incluye notas asociadas al paciente
    """
    return await PatientService.get_patient_by_id(db, patient_id)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo paciente"
)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo paciente en el sistema

    **Para DNI:**
    - **document_type**: "DNI"
    - **document_number**: 8 dígitos
    - **first_name**: Requerido
    - **last_name**: Requerido
    - **business_name**: No aplica (dejar vacío)

    **Para RUC:**
    - **document_type**: "RUC"
    - **document_number**: 11 dígitos
    - **business_name**: Requerido
    - **first_name**: No aplica (dejar vacío)
    - **last_name**: No aplica (dejar vacío)

    **Campos opcionales:**
    - **phone**: Teléfono
    - **email**: Email
    - **address**: Dirección
    """
    return await PatientService.create_patient(db, data)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Actualizar paciente"
)
async def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información de contacto de un paciente

    **Nota:** No se puede cambiar el tipo o número de documento
    Solo se pueden actualizar datos de contacto y estado
    """
    return await PatientService.update_patient(db, patient_id, data)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_200_OK,
    summary="Desactivar paciente"
)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Desactivar un paciente (soft delete)

    **Nota:** Esto marca al paciente como inactivo, no lo elimina físicamente
    """
    return await PatientService.delete_patient(db, patient_id)


@router.post(
    "/{patient_id}/notes",
    response_model=PatientNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar nota a paciente"
)
async def add_note_to_patient(
    patient_id: int,
    data: PatientNoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Agregar una nota al historial del paciente

    Las notas pueden usarse para registrar:
    - Observaciones médicas
    - Alertas importantes
    - Preferencias del paciente
    - Cualquier información relevante
    """
    return await PatientService.add_note_to_patient(db, patient_id, data)


@router.get(
    "/{patient_id}/notes",
    response_model=List[PatientNoteResponse],
    summary="Obtener notas del paciente"
)
async def get_patient_notes(
    patient_id: int,
    limit: int = Query(10, ge=1, le=50, description="Número máximo de notas a retornar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener notas asociadas a un paciente

    Las notas se retornan ordenadas por fecha de creación (más reciente primero)
    """
    return await PatientService.get_patient_notes(db, patient_id, limit)

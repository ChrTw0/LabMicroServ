"""
Patient Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from src.models.patient import DocumentType


# ==================== Patient Schemas ====================

class PatientBase(BaseModel):
    """Base patient schema"""
    document_type: DocumentType = Field(..., description="Tipo de documento (DNI o RUC)")
    document_number: str = Field(..., min_length=8, max_length=11, description="Número de documento")

    # Datos personales (para DNI)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombres (requerido para DNI)")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Apellidos (requerido para DNI)")

    # Datos empresa (para RUC)
    business_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Razón social (requerido para RUC)")

    # Contacto
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    email: Optional[str] = Field(None, max_length=255, description="Email")
    address: Optional[str] = Field(None, max_length=255, description="Dirección")

    @validator('document_number')
    def validate_document_number(cls, v, values):
        """Validate document number length based on type"""
        if 'document_type' in values:
            doc_type = values['document_type']
            if doc_type == DocumentType.DNI and len(v) != 8:
                raise ValueError('DNI debe tener exactamente 8 dígitos')
            if doc_type == DocumentType.RUC and len(v) != 11:
                raise ValueError('RUC debe tener exactamente 11 dígitos')
            if not v.isdigit():
                raise ValueError('El número de documento debe contener solo dígitos')
        return v

    @validator('first_name', always=True)
    def validate_first_name(cls, v, values):
        """First name is required for DNI"""
        if 'document_type' in values and values['document_type'] == DocumentType.DNI:
            if not v:
                raise ValueError('Nombres son requeridos para DNI')
        return v

    @validator('last_name', always=True)
    def validate_last_name(cls, v, values):
        """Last name is required for DNI"""
        if 'document_type' in values and values['document_type'] == DocumentType.DNI:
            if not v:
                raise ValueError('Apellidos son requeridos para DNI')
        return v

    @validator('business_name', always=True)
    def validate_business_name(cls, v, values):
        """Business name is required for RUC"""
        if 'document_type' in values and values['document_type'] == DocumentType.RUC:
            if not v:
                raise ValueError('Razón social es requerida para RUC')
        return v


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient (RF-010)"""
    # Contacto (solo datos actualizables)
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    email: Optional[str] = Field(None, max_length=255, description="Email")
    address: Optional[str] = Field(None, max_length=255, description="Dirección")

    # Estado
    is_active: Optional[bool] = None


class PatientResponse(BaseModel):
    """Schema for patient response"""
    id: int
    document_type: DocumentType
    document_number: str
    first_name: Optional[str]
    last_name: Optional[str]
    business_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    is_recurrent: bool
    visit_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PatientDetailResponse(PatientResponse):
    """Detailed patient response with notes"""
    notes: List["PatientNoteResponse"] = Field(default_factory=list)


class PatientListResponse(BaseModel):
    """Paginated list of patients"""
    total: int = Field(..., description="Total de pacientes")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    patients: List[PatientResponse] = Field(..., description="Lista de pacientes")


# ==================== Patient Note Schemas ====================

class PatientNoteCreate(BaseModel):
    """Schema for creating a patient note"""
    note: str = Field(..., min_length=1, description="Contenido de la nota")


class PatientNoteResponse(BaseModel):
    """Schema for patient note response"""
    id: int
    patient_id: int
    note: str
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Patient History Schemas ====================

class PatientHistoryResponse(BaseModel):
    """Schema for patient history response"""
    id: int
    patient_id: int
    order_id: int
    action: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Update forward references
PatientDetailResponse.model_rebuild()

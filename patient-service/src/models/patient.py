"""
Patient Service Models
Database: patient_db
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class DocumentType(str, enum.Enum):
    """Tipos de documento"""
    DNI = "DNI"
    RUC = "RUC"


class Patient(Base):
    """Paciente"""
    __tablename__ = "patients"
    __table_args__ = (
        Index('ix_patients_document_number', 'document_number'),
        Index('ix_patients_first_name_last_name', 'first_name', 'last_name'),
        Index('ix_patients_is_recurrent', 'is_recurrent'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Documento
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, native_enum=False),
        nullable=False
    )
    document_number: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)

    # Datos personales (DNI)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Datos empresa (RUC)
    business_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Contacto
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Metadata
    is_recurrent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Auditoría (referencias lógicas a user_db.users)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    history: Mapped[List["PatientHistory"]] = relationship(
        "PatientHistory",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    notes: Mapped[List["PatientNote"]] = relationship(
        "PatientNote",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        name = self.business_name if self.document_type == DocumentType.RUC else f"{self.first_name} {self.last_name}"
        return f"<Patient(id={self.id}, doc={self.document_number}, name='{name}')>"


class PatientHistory(Base):
    """Historial de acciones del paciente"""
    __tablename__ = "patient_history"
    __table_args__ = (
        Index('ix_patient_history_patient_id', 'patient_id'),
        Index('ix_patient_history_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)

    # Referencia lógica a order_db.orders
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Datos
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    patient: Mapped["Patient"] = relationship("Patient", back_populates="history")

    def __repr__(self):
        return f"<PatientHistory(patient_id={self.patient_id}, order_id={self.order_id})>"


class PatientNote(Base):
    """Notas sobre el paciente"""
    __tablename__ = "patient_notes"
    __table_args__ = (
        Index('ix_patient_notes_patient_id', 'patient_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)

    # Datos
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Auditoría (referencia lógica a user_db.users)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    patient: Mapped["Patient"] = relationship("Patient", back_populates="notes")

    def __repr__(self):
        return f"<PatientNote(id={self.id}, patient_id={self.patient_id})>"

"""
Billing Models
"""
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import enum

from src.core.database import Base

class InvoiceType(str, enum.Enum):
    BOLETA = "BOLETA"
    FACTURA = "FACTURA"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        Index('ix_invoices_issue_date', 'issue_date'),  # índice explícito solo para issue_date
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    # Referencias lógicas a otros servicios
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # mantiene index=True
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Datos del comprobante
    invoice_type: Mapped[InvoiceType] = mapped_column(SQLEnum(InvoiceType, native_enum=False), nullable=False)
    invoice_status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus, native_enum=False), default=InvoiceStatus.PENDING, index=True)

    # Datos del cliente (desnormalizado para el comprobante)
    customer_document_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DNI o RUC
    customer_document_number: Mapped[str] = mapped_column(String(11), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Montos
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Fechas
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")

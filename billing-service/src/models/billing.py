"""
Billing & Reconciliation Service Models
Database: billing_db (Shared)
"""
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Date, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base

# --- Billing Models ---

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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    invoice_type: Mapped[InvoiceType] = mapped_column(SQLEnum(InvoiceType, native_enum=False), nullable=False)
    invoice_status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus, native_enum=False), nullable=False, default=InvoiceStatus.DRAFT, index=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    credit_note: Mapped["CreditNote"] = relationship("CreditNote", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")

class CreditNote(Base):
    __tablename__ = "credit_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="credit_note")

# --- Reconciliation Models ---

class ClosureStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"

class DailyClosure(Base):
    __tablename__ = "daily_closures"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    closure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ClosureStatus] = mapped_column(SQLEnum(ClosureStatus, native_enum=False), nullable=False, default=ClosureStatus.OPEN, index=True)
    expected_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    registered_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    difference: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    discrepancies: Mapped[List["Discrepancy"]] = relationship("Discrepancy", back_populates="closure", cascade="all, delete-orphan")

class Discrepancy(Base):
    __tablename__ = "discrepancies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    closure_id: Mapped[int] = mapped_column(ForeignKey('daily_closures.id'), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closure: Mapped["DailyClosure"] = relationship("DailyClosure", back_populates="discrepancies")
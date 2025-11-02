"""
Reconciliation Models
"""
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Date, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
import enum

from src.core.database import Base

class ClosureStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"

class DailyClosure(Base):
    __tablename__ = "daily_closures"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    closure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ClosureStatus] = mapped_column(SQLEnum(ClosureStatus, native_enum=False), default=ClosureStatus.OPEN, index=True)
    expected_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    registered_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    difference: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    discrepancies: Mapped[List["Discrepancy"]] = relationship("Discrepancy", back_populates="closure", cascade="all, delete-orphan")

class Discrepancy(Base):
    __tablename__ = "discrepancies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    closure_id: Mapped[int] = mapped_column(ForeignKey('daily_closures.id'), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    closure: Mapped["DailyClosure"] = relationship("DailyClosure", back_populates="discrepancies")

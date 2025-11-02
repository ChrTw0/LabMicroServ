"""
Lab Integration Models
"""
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum

from src.core.database import Base

class SyncStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class LabSyncLog(Base):
    __tablename__ = "lab_sync_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus, native_enum=False), default=SyncStatus.PENDING, index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    order: Mapped["Order"] = relationship("Order", back_populates="lab_sync_log")

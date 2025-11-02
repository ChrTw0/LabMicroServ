"""
Core Service Models (Fused)
Contains models for Configuration and Notifications
Database: config_db
"""
from datetime import datetime
from typing import Optional, List
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base

# --- Configuration Models ---

class CompanyInfo(Base):
    __tablename__ = "company_info"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ruc: Mapped[str] = mapped_column(String(11), nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

# --- Notification Models ---

class NotificationType(str, enum.Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"

class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class TemplateType(str, enum.Enum):
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"
    INVOICE_RECEIPT = "INVOICE_RECEIPT"

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType, native_enum=False), nullable=False, index=True)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus, native_enum=False), nullable=False, default=NotificationStatus.PENDING, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_type: Mapped[TemplateType] = mapped_column(SQLEnum(TemplateType, native_enum=False), unique=True, nullable=False, index=True)
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
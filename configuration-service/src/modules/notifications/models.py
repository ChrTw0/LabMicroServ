"""
Notification Models
"""
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import enum

from src.core.database import Base

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
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType, native_enum=False), index=True)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus, native_enum=False), default=NotificationStatus.PENDING, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_type: Mapped[TemplateType] = mapped_column(SQLEnum(TemplateType, native_enum=False), unique=True, index=True)
    subject_template: Mapped[str] = mapped_column(String(255))
    body_template: Mapped[str] = mapped_column(Text)

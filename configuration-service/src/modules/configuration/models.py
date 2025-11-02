"""
Configuration Models
"""
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from src.core.database import Base

class CompanyInfo(Base):
    __tablename__ = "company_info"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ruc: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

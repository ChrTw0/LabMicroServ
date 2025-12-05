from sqlalchemy import (Column, Integer, String, Boolean, Numeric, Text,
                        ForeignKey, DateTime, func)
from sqlalchemy.orm import relationship
from src.core.database import Base

class Category(Base):
    __tablename__ = "catalog_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    tests = relationship("Test", back_populates="category")

class SampleType(Base):
    __tablename__ = "catalog_sample_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    tests = relationship("Test", back_populates="sample_type")

class Test(Base):
    __tablename__ = "catalog_tests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    category_id = Column(Integer, ForeignKey("catalog_categories.id"), nullable=False)
    sample_type_id = Column(Integer, ForeignKey("catalog_sample_types.id"), nullable=False)
    
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    
    turnaround_time = Column(String(100)) # e.g., "24-48 hours"
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    category = relationship("Category", back_populates="tests")
    sample_type = relationship("SampleType", back_populates="tests")

    # Relationships to other modules (Orders) would go here
    # order_items = relationship("OrderItem", back_populates="test")
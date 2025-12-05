from sqlalchemy import (Column, Integer, String, Boolean, Numeric, Text,
                        ForeignKey, DateTime, func, Enum as SQLAlchemyEnum)
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "Pendiente"
    IN_PROGRESS = "En Proceso"
    COMPLETED = "Completada"
    CANCELLED = "Cancelada"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(20), unique=True, index=True, nullable=False)
    
    patient_id = Column(Integer, nullable=False, index=True) # Foreign key to patient-service (conceptual)
    referring_doctor_name = Column(String(255))
    
    location_id = Column(Integer, nullable=False) # Foreign key to configuration-service (conceptual)
    
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0.0)
    final_amount = Column(Numeric(10, 2), nullable=False)
    
    status = Column(SQLAlchemyEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    created_by_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("OrderPayment", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    test_id = Column(Integer, ForeignKey("catalog_tests.id"), nullable=False)
    test_name = Column(String(255), nullable=False)
    test_code = Column(String(50), nullable=False)
    
    price = Column(Numeric(10, 2), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="items")
    test = relationship("Test", backref="order_items")

class OrderPayment(Base):
    __tablename__ = "order_payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False) # e.g., 'Efectivo', 'Tarjeta', 'Yape'
    reference = Column(String(255)) # e.g., transaction ID
    
    created_at = Column(DateTime, server_default=func.now())
    
    order = relationship("Order", back_populates="payments")
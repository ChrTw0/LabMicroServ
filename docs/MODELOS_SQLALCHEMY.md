# 🗄️ Modelos SQLAlchemy 2.0 - Sistema de Laboratorio Clínico

**Versión:** 3.0 (Arquitectura Refactorizada - 5 DBs - 7 Microservicios)
**Fecha:** 2025-10-31
**ORM:** SQLAlchemy 2.0 Async

---

## 📚 Índice

1. [user_db - User Service](#1-user_db---user-service)
2. [patient_db - Patient Service](#2-patient_db---patient-service)
3. [order_db - Order Service ⭐ (Fusionado: Catalog + Orders + Lab Integration)](#3-order_db---order-service-)
4. [billing_db - Billing Service ⭐ (Fusionado: Billing + Reconciliation)](#4-billing_db---billing-service-)
5. [config_db - Core Service ⭐ (Fusionado: Configuration + Notification)](#5-config_db---core-service-)

---

## 1. user_db - User Service

### `user-service/src/models/user.py`

```python
"""
User Service Models
Database: user_db
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class User(Base):
    """Usuario del sistema"""
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos básicos
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Estado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Referencia lógica a config_db.locations (sin FK)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Auditoría
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
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"


class Role(Base):
    """Roles del sistema"""
    __tablename__ = "roles"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    # Valores: 'Administrador General', 'Recepcionista', 'Supervisor de Sede', 'Laboratorista'
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    permissions: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="role"
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class UserRole(Base):
    """Tabla intermedia User <-> Role (N:N)"""
    __tablename__ = "user_roles"
    __table_args__ = (
        Index('ix_user_roles_user_id', 'user_id'),
        Index('ix_user_roles_role_id', 'role_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Auditoría
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    assigned_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class PasswordResetToken(Base):
    """Tokens para recuperación de contraseña"""
    __tablename__ = "password_reset_tokens"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Datos
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, expires_at={self.expires_at})>"


class AuditLog(Base):
    """Registro de auditoría de acciones"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('ix_audit_logs_user_id', 'user_id'),
        Index('ix_audit_logs_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Datos
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Ejemplos: 'LOGIN', 'LOGOUT', 'CREATE_USER', 'UPDATE_ROLE', etc.
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    old_values: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    new_values: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
```

---

## 2. patient_db - Patient Service

### `patient-service/src/models/patient.py`

```python
"""
Patient Service Models
Database: patient_db
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Enum as SQLEnum, Index
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
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)

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
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)

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
```

---

## 3. order_db - Order Service ⭐

> **FUSIÓN:** Este servicio integra 3 bounded contexts cohesivos:
> - **Catalog Module:** Catálogo de servicios/exámenes y precios
> - **Orders Module:** Órdenes de servicio y pagos
> - **Lab Integration Module:** Sincronización con sistema de laboratorio (event-driven)

**Base de datos:** `order_db` (Puerto: 5435)
**Servicio:** `order-service` (Puerto: 8004)
**Justificación de fusión:** El catálogo solo existe para crear órdenes, y la integración con laboratorio se dispara al crear/actualizar órdenes.

---

### `order-service/src/modules/catalog/models.py`

```python
"""
Catalog Module Models
Database: order_db
Module: catalog (dentro de order-service)
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class Category(Base):
    """Categoría de servicios/exámenes"""
    __tablename__ = "categories"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Auditoría
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

    # Relaciones
    services: Mapped[List["Service"]] = relationship(
        "Service",
        back_populates="category"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, code='{self.code}', name='{self.name}')>"


class Service(Base):
    """Servicio/Examen del catálogo"""
    __tablename__ = "services"
    __table_args__ = (
        Index('ix_services_code', 'code'),
        Index('ix_services_name', 'name'),
        Index('ix_services_category_id', 'category_id'),
        Index('ix_services_is_active', 'is_active'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Key
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Precio
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Estado
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
    category: Mapped["Category"] = relationship("Category", back_populates="services")
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="service",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Service(id={self.id}, code='{self.code}', name='{self.name}', price={self.current_price})>"


class PriceHistory(Base):
    """Historial de cambios de precio"""
    __tablename__ = "price_history"
    __table_args__ = (
        Index('ix_price_history_service_id', 'service_id'),
        Index('ix_price_history_changed_at', 'changed_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    service_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    old_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    new_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Auditoría (referencia lógica a user_db.users)
    changed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    service: Mapped["Service"] = relationship("Service", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory(service_id={self.service_id}, {self.old_price} -> {self.new_price})>"
```

---

### `order-service/src/modules/orders/models.py`

```python
"""
Orders Module Models
Database: order_db
Module: orders (dentro de order-service)
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class OrderStatus(str, enum.Enum):
    """Estados de la orden"""
    REGISTRADA = "REGISTRADA"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"
    ANULADA = "ANULADA"


class PaymentMethod(str, enum.Enum):
    """Métodos de pago"""
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    YAPE_PLIN = "YAPE_PLIN"


class DiscountType(str, enum.Enum):
    """Tipos de descuento"""
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"


class Order(Base):
    """Orden de servicio"""
    __tablename__ = "orders"
    __table_args__ = (
        Index('ix_orders_order_number', 'order_number'),
        Index('ix_orders_patient_id', 'patient_id'),
        Index('ix_orders_location_id', 'location_id'),
        Index('ix_orders_status', 'status'),
        Index('ix_orders_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Número único (formato: SEDE-AAAA-NNNNNN, ej: LIM01-2025-000123)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Referencias lógicas (sin FK)
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → patient_db.patients
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → config_db.locations

    # Estado
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.REGISTRADA
    )

    # Montos
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    igv_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # Ej: 18.00
    igv_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Anulación
    cancelled_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users

    # Auditoría
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
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    payments: Mapped[List["OrderPayment"]] = relationship(
        "OrderPayment",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    discounts: Mapped[List["OrderDiscount"]] = relationship(
        "OrderDiscount",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    status_history: Mapped[List["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    lab_sync_logs: Mapped[List["LabSyncLog"]] = relationship(
        "LabSyncLog",
        back_populates="order"
    )

    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status={self.status}, total={self.total})>"


class OrderItem(Base):
    """Items/servicios de una orden"""
    __tablename__ = "order_items"
    __table_args__ = (
        Index('ix_order_items_order_id', 'order_id'),
        Index('ix_order_items_service_id', 'service_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Referencia lógica a catalog_db.services
    service_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos desnormalizados (para histórico)
    service_code: Mapped[str] = mapped_column(String(50), nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cantidades
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, service='{self.service_name}', qty={self.quantity})>"


class OrderPayment(Base):
    """Métodos de pago de una orden (1:N - permite pago mixto)"""
    __tablename__ = "order_payments"
    __table_args__ = (
        Index('ix_order_payments_order_id', 'order_id'),
        Index('ix_order_payments_payment_method', 'payment_method'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod, native_enum=False),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Auditoría
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    registered_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<OrderPayment(order_id={self.order_id}, method={self.payment_method}, amount={self.amount})>"


class OrderDiscount(Base):
    """Descuentos aplicados a una orden (1:N - permite múltiples descuentos)"""
    __tablename__ = "order_discounts"
    __table_args__ = (
        Index('ix_order_discounts_order_id', 'order_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    discount_type: Mapped[DiscountType] = mapped_column(
        SQLEnum(DiscountType, native_enum=False),
        nullable=False
    )
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Auditoría
    applied_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="discounts")

    def __repr__(self):
        return f"<OrderDiscount(order_id={self.order_id}, type={self.discount_type}, amount={self.discount_amount})>"


class OrderStatusHistory(Base):
    """Historial de cambios de estado de orden"""
    __tablename__ = "order_status_history"
    __table_args__ = (
        Index('ix_order_status_history_order_id', 'order_id'),
        Index('ix_order_status_history_changed_at', 'changed_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    old_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auditoría
    changed_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="status_history")

    def __repr__(self):
        return f"<OrderStatusHistory(order_id={self.order_id}, {self.old_status} -> {self.new_status})>"
```

---

### `order-service/src/modules/lab_integration/models.py`

```python
"""
Lab Integration Module Models
Database: order_db
Module: lab_integration (dentro de order-service)
Patrón: Event-driven consumer (escucha eventos de order.created, order.updated)
"""
from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class SyncStatus(str, enum.Enum):
    """Estados de sincronización"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class LabSyncLog(Base):
    """Log de sincronización con sistema de laboratorio"""
    __tablename__ = "lab_sync_logs"
    __table_args__ = (
        Index('ix_lab_sync_logs_order_id', 'order_id'),
        Index('ix_lab_sync_logs_sync_status', 'sync_status'),
        Index('ix_lab_sync_logs_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key a orders (READ-ONLY desde lab-integration)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    # Estado de sincronización
    sync_status: Mapped[SyncStatus] = mapped_column(
        SQLEnum(SyncStatus, native_enum=False),
        nullable=False,
        default=SyncStatus.PENDING
    )

    # Reintentos
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Payloads
    request_payload: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    response_payload: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relación con Order (importar desde order-service)
    # NOTA: Esto requiere que Order esté definido primero
    order: Mapped["Order"] = relationship("Order", back_populates="lab_sync_logs")

    def __repr__(self):
        return f"<LabSyncLog(id={self.id}, order_id={self.order_id}, status={self.sync_status}, attempts={self.attempt_count})>"
```

---

## 4. billing_db - Billing Service ⭐

> **FUSIÓN:** Este servicio integra 2 bounded contexts cohesivos:
> - **Billing Module:** Facturación electrónica y comprobantes SUNAT
> - **Reconciliation Module:** Conciliación diaria y cierre de caja

**Base de datos:** `billing_db` (Puerto: 5436)
**Servicio:** `billing-service` (Puerto: 8005)
**Justificación de fusión:** La conciliación es la culminación del ciclo diario de facturación, ambos trabajan sobre los mismos comprobantes y cierres.

---

### `billing-service/src/modules/billing/models.py`

```python
"""
Billing Module Models
Database: billing_db
Module: billing (dentro de billing-service)
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class InvoiceType(str, enum.Enum):
    """Tipos de comprobante"""
    BOLETA = "BOLETA"  # Boleta de Venta Electrónica
    FACTURA = "FACTURA"  # Factura Electrónica


class InvoiceStatus(str, enum.Enum):
    """Estados del comprobante"""
    DRAFT = "DRAFT"  # Borrador
    PENDING = "PENDING"  # Pendiente de envío a SUNAT
    SENT = "SENT"  # Enviado a SUNAT
    ACCEPTED = "ACCEPTED"  # Aceptado por SUNAT
    REJECTED = "REJECTED"  # Rechazado por SUNAT
    CANCELLED = "CANCELLED"  # Anulado (con nota de crédito)


class Invoice(Base):
    """Comprobante electrónico (Boleta o Factura)"""
    __tablename__ = "invoices"
    __table_args__ = (
        Index('ix_invoices_invoice_number', 'invoice_number'),
        Index('ix_invoices_order_id', 'order_id'),
        Index('ix_invoices_invoice_type', 'invoice_type'),
        Index('ix_invoices_invoice_status', 'invoice_status'),
        Index('ix_invoices_issue_date', 'issue_date'),
        Index('ix_invoices_location_id', 'location_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Número de comprobante (formato SUNAT: SERIE-CORRELATIVO, ej: B001-00000123, F001-00000045)
    invoice_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Tipo de comprobante
    invoice_type: Mapped[InvoiceType] = mapped_column(
        SQLEnum(InvoiceType, native_enum=False),
        nullable=False
    )

    # Estado
    invoice_status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, native_enum=False),
        nullable=False,
        default=InvoiceStatus.DRAFT
    )

    # Referencias lógicas (sin FK)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # → order_db.orders
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → patient_db.patients
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → config_db.locations

    # Datos del cliente (desnormalizados para histórico)
    customer_document_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DNI/RUC
    customer_document_number: Mapped[str] = mapped_column(String(11), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Montos
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    igv_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    igv_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Datos SUNAT
    serie: Mapped[str] = mapped_column(String(4), nullable=False)  # Ej: B001, F001
    correlative: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Hash del XML
    qr_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # QR code base64

    # Archivos
    xml_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cdr_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # CDR de SUNAT

    # Fechas
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoría
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
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    sunat_responses: Mapped[List["SunatResponse"]] = relationship(
        "SunatResponse",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    credit_notes: Mapped[List["CreditNote"]] = relationship(
        "CreditNote",
        back_populates="invoice"
    )
    audit_logs: Mapped[List["InvoiceAudit"]] = relationship(
        "InvoiceAudit",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', type={self.invoice_type}, status={self.invoice_status}, total={self.total})>"


class InvoiceItem(Base):
    """Items/servicios de un comprobante"""
    __tablename__ = "invoice_items"
    __table_args__ = (
        Index('ix_invoice_items_invoice_id', 'invoice_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    invoice_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos del servicio (desnormalizados)
    service_code: Mapped[str] = mapped_column(String(50), nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relaciones
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem(invoice_id={self.invoice_id}, service='{self.service_name}', qty={self.quantity})>"


class SunatResponse(Base):
    """Respuestas de SUNAT/PSE"""
    __tablename__ = "sunat_responses"
    __table_args__ = (
        Index('ix_sunat_responses_invoice_id', 'invoice_id'),
        Index('ix_sunat_responses_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    invoice_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Respuesta SUNAT
    response_code: Mapped[str] = mapped_column(String(10), nullable=False)  # Ej: 0 (éxito), 4000 (error)
    response_message: Mapped[str] = mapped_column(Text, nullable=False)
    cdr_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # XML del CDR
    cdr_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    raw_response: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="sunat_responses")

    def __repr__(self):
        return f"<SunatResponse(invoice_id={self.invoice_id}, code='{self.response_code}', success={self.is_success})>"


class CreditNote(Base):
    """Nota de crédito (anulación de comprobante)"""
    __tablename__ = "credit_notes"
    __table_args__ = (
        Index('ix_credit_notes_credit_note_number', 'credit_note_number'),
        Index('ix_credit_notes_invoice_id', 'invoice_id'),
        Index('ix_credit_notes_issue_date', 'issue_date'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Número de nota de crédito (formato SUNAT)
    credit_note_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Foreign Key
    invoice_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    reason: Mapped[str] = mapped_column(Text, nullable=False)  # Motivo de anulación
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Archivos SUNAT
    xml_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cdr_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Fechas
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users

    # Relaciones
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="credit_notes")

    def __repr__(self):
        return f"<CreditNote(id={self.id}, number='{self.credit_note_number}', invoice_id={self.invoice_id})>"


class InvoiceAudit(Base):
    """Auditoría de cambios en comprobantes"""
    __tablename__ = "invoice_audit"
    __table_args__ = (
        Index('ix_invoice_audit_invoice_id', 'invoice_id'),
        Index('ix_invoice_audit_created_at', 'created_at'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    invoice_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Datos
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    # Ejemplos: 'CREATED', 'SENT_TO_SUNAT', 'ACCEPTED', 'REJECTED', 'CANCELLED'
    old_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auditoría
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="audit_logs")

    def __repr__(self):
        return f"<InvoiceAudit(invoice_id={self.invoice_id}, action='{self.action}')>"
```

---

### `billing-service/src/modules/reconciliation/models.py`

```python
"""
Reconciliation Module Models
Database: billing_db
Module: reconciliation (dentro de billing-service)
"""
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Numeric, Text, Date, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class ClosureStatus(str, enum.Enum):
    """Estados del cierre de caja"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class DiscrepancyType(str, enum.Enum):
    """Tipos de discrepancia"""
    MISSING_INVOICE = "MISSING_INVOICE"  # Orden sin comprobante
    MISSING_ORDER = "MISSING_ORDER"  # Comprobante sin orden
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"  # Montos no coinciden
    PAYMENT_MISMATCH = "PAYMENT_MISMATCH"  # Pagos no coinciden


class DailyClosure(Base):
    """Cierre diario de caja por sede"""
    __tablename__ = "daily_closures"
    __table_args__ = (
        Index('ix_daily_closures_location_id_closure_date', 'location_id', 'closure_date'),
        Index('ix_daily_closures_status', 'status'),
        Index('ix_daily_closures_closure_date', 'closure_date'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Referencias lógicas
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → config_db.locations

    # Fecha del cierre
    closure_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Estado
    status: Mapped[ClosureStatus] = mapped_column(
        SQLEnum(ClosureStatus, native_enum=False),
        nullable=False,
        default=ClosureStatus.OPEN
    )

    # Conteos
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_invoices: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_discrepancies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Montos esperados (desde órdenes)
    expected_cash: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    expected_card: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    expected_transfer: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    expected_yape_plin: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    expected_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    # Montos registrados (desde comprobantes)
    registered_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    # Diferencia
    difference: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cierre
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users

    # Reapertura
    reopened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reopened_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users
    reopen_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auditoría
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

    # Relaciones
    cash_counts: Mapped[List["CashCount"]] = relationship(
        "CashCount",
        back_populates="closure",
        cascade="all, delete-orphan"
    )
    discrepancies: Mapped[List["Discrepancy"]] = relationship(
        "Discrepancy",
        back_populates="closure",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DailyClosure(id={self.id}, location_id={self.location_id}, date={self.closure_date}, status={self.status})>"


class CashCount(Base):
    """Conteo de efectivo por denominación"""
    __tablename__ = "cash_counts"
    __table_args__ = (
        Index('ix_cash_counts_closure_id', 'closure_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    closure_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Conteo físico de efectivo
    # Billetes
    count_200: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_100: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_50: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_20: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_10: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Monedas
    count_5: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_2: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_1: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_050: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0.50
    count_020: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0.20
    count_010: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0.10

    # Total contado
    total_counted: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Auditoría
    counted_by: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users
    counted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    closure: Mapped["DailyClosure"] = relationship("DailyClosure", back_populates="cash_counts")

    def __repr__(self):
        return f"<CashCount(closure_id={self.closure_id}, total={self.total_counted})>"


class Discrepancy(Base):
    """Discrepancia encontrada en la conciliación"""
    __tablename__ = "discrepancies"
    __table_args__ = (
        Index('ix_discrepancies_closure_id', 'closure_id'),
        Index('ix_discrepancies_discrepancy_type', 'discrepancy_type'),
        Index('ix_discrepancies_is_resolved', 'is_resolved'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign Key
    closure_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tipo de discrepancia
    discrepancy_type: Mapped[DiscrepancyType] = mapped_column(
        SQLEnum(DiscrepancyType, native_enum=False),
        nullable=False
    )

    # Referencias lógicas
    order_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → order_db.orders
    invoice_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → billing_db.invoices

    # Detalles
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    actual_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    difference_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Resolución
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    closure: Mapped["DailyClosure"] = relationship("DailyClosure", back_populates="discrepancies")

    def __repr__(self):
        return f"<Discrepancy(id={self.id}, type={self.discrepancy_type}, resolved={self.is_resolved})>"
```

---

## 5. config_db - Core Service ⭐

> **FUSIÓN:** Este servicio integra 2 bounded contexts utilitarios:
> - **Configuration Module:** Configuración del sistema, sedes, empresa
> - **Notification Module:** Gestión de notificaciones y templates

**Base de datos:** `config_db` (Puerto: 5437)
**Servicio:** `core-service` (Puerto: 8010)
**Justificación de fusión:** Ambos son servicios utilitarios de soporte transversal, las plantillas de notificación son parte de la configuración del sistema.

---

### `core-service/src/modules/configuration/models.py`

```python
"""
Configuration Module Models
Database: config_db
Module: configuration (dentro de core-service)
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class CompanyInfo(Base):
    """Información de la empresa (singleton)"""
    __tablename__ = "company_info"

    # Primary Key (solo existirá 1 registro)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos legales
    ruc: Mapped[str] = mapped_column(String(11), nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Logo
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Configuración fiscal
    igv_percentage: Mapped[str] = mapped_column(String(5), nullable=False, default="18.00")

    # Auditoría
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
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → user_db.users

    def __repr__(self):
        return f"<CompanyInfo(ruc='{self.ruc}', name='{self.business_name}')>"


class Location(Base):
    """Sedes/sucursales"""
    __tablename__ = "locations"
    __table_args__ = (
        Index('ix_locations_code', 'code'),
        Index('ix_locations_is_active', 'is_active'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # Ej: LIM01, CUS02
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Configuración de facturación
    invoice_serie: Mapped[str] = mapped_column(String(4), nullable=False)  # Ej: F001
    receipt_serie: Mapped[str] = mapped_column(String(4), nullable=False)  # Ej: B001
    next_invoice_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    next_receipt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Estado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Auditoría
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

    def __repr__(self):
        return f"<Location(id={self.id}, code='{self.code}', name='{self.name}')>"


class SystemSetting(Base):
    """Configuraciones del sistema (key-value)"""
    __tablename__ = "system_settings"
    __table_args__ = (
        Index('ix_system_settings_key', 'key'),
        Index('ix_system_settings_category', 'category'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # Categorías: 'SUNAT', 'SMTP', 'WHATSAPP', 'GENERAL', 'BACKUP', etc.
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Auditoría
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
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"<SystemSetting(key='{self.key}', category='{self.category}')>"


class BackupLog(Base):
    """Registro de backups realizados"""
    __tablename__ = "backup_logs"
    __table_args__ = (
        Index('ix_backup_logs_backup_date', 'backup_date'),
        Index('ix_backup_logs_is_success', 'is_success'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Datos del backup
    backup_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    backup_type: Mapped[str] = mapped_column(String(20), nullable=False)  # FULL, INCREMENTAL
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Estado
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    databases_backed_up: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"<BackupLog(id={self.id}, date={self.backup_date}, success={self.is_success})>"
```

---

### `core-service/src/modules/notification/models.py`

```python
"""
Notification Module Models
Database: config_db
Module: notification (dentro de core-service)
"""
from datetime import datetime
from typing import Optional, List
import enum
from sqlalchemy import String, Boolean, Integer, DateTime, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificación"""
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    ALERT = "ALERT"  # Alertas internas (email + SMS)


class NotificationStatus(str, enum.Enum):
    """Estados de envío"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class TemplateType(str, enum.Enum):
    """Tipos de plantilla"""
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"
    INVOICE_RECEIPT = "INVOICE_RECEIPT"
    PAYMENT_CONFIRMATION = "PAYMENT_CONFIRMATION"
    RECONCILIATION_ALERT = "RECONCILIATION_ALERT"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    PASSWORD_RESET = "PASSWORD_RESET"


class NotificationLog(Base):
    """Registro de notificaciones enviadas"""
    __tablename__ = "notification_logs"
    __table_args__ = (
        Index('ix_notification_logs_notification_type', 'notification_type'),
        Index('ix_notification_logs_status', 'status'),
        Index('ix_notification_logs_created_at', 'created_at'),
        Index('ix_notification_logs_recipient_id', 'recipient_id'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Tipo y estado
    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, native_enum=False),
        nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus, native_enum=False),
        nullable=False,
        default=NotificationStatus.PENDING
    )

    # Referencia lógica a plantilla (opcional)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Destinatario
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # → patient_db.patients o user_db.users
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Contenido
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    html_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Para emails

    # Attachments (opcional)
    attachments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as TEXT

    # Reintentos
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Respuesta del proveedor
    provider_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON as TEXT

    def __repr__(self):
        return f"<NotificationLog(id={self.id}, type={self.notification_type}, status={self.status}, recipient={self.recipient_email})>"


class NotificationTemplate(Base):
    """Plantillas de notificaciones"""
    __tablename__ = "notification_templates"
    __table_args__ = (
        Index('ix_notification_templates_template_type', 'template_type'),
        Index('ix_notification_templates_is_active', 'is_active'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Tipo
    template_type: Mapped[TemplateType] = mapped_column(
        SQLEnum(TemplateType, native_enum=False),
        nullable=False
    )

    # Datos
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Subject (para emails)
    subject_template: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Contenido
    body_template: Mapped[str] = mapped_column(Text, nullable=False)  # Puede contener variables {{ variable }}
    html_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # HTML para emails

    # Variables esperadas
    required_variables: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as TEXT

    # Estado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Auditoría
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

    def __repr__(self):
        return f"<NotificationTemplate(id={self.id}, type={self.template_type}, name='{self.name}')>"


class NotificationRecipient(Base):
    """Destinatarios de alertas del sistema (supervisores, admins)"""
    __tablename__ = "notification_recipients"
    __table_args__ = (
        Index('ix_notification_recipients_user_id', 'user_id'),
        Index('ix_notification_recipients_alert_type', 'alert_type'),
    )

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Referencia lógica
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # → user_db.users

    # Tipo de alerta que debe recibir
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Ejemplos: 'RECONCILIATION_DISCREPANCY', 'SYSTEM_ERROR', 'BACKUP_FAILED', etc.

    # Canales habilitados
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notify_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Estado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Auditoría
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

    def __repr__(self):
        return f"<NotificationRecipient(user_id={self.user_id}, alert_type='{self.alert_type}')>"
```

---

## 📝 Resumen Final

### ✅ Bases de Datos Completadas

| # | Base de Datos | Servicios | Tablas | Estado |
|---|---------------|-----------|--------|--------|
| 1 | **user_db** | user-service | 5 | ✅ Completo |
| 2 | **patient_db** | patient-service | 3 | ✅ Completo |
| 3 | **catalog_db** | catalog-service | 3 | ✅ Completo |
| 4 | **order_db** ⭐ | order-service + lab-integration | 6 | ✅ Completo |
| 5 | **billing_db** ⭐ | billing-service + reconciliation | 8 | ✅ Completo |
| 6 | **config_db** ⭐ | configuration + notification | 7 | ✅ Completo |

**Total: 6 bases de datos, 32 tablas**

---

### 🎯 Características Implementadas

#### **Patrones SQLAlchemy 2.0:**
✅ `Mapped[]` type hints (PEP 484)
✅ `mapped_column()` en lugar de `Column()`
✅ `DeclarativeBase` en lugar de `declarative_base()`
✅ Relaciones tipadas con `Mapped[List["Model"]]`
✅ Enums nativos con `str, enum.Enum`
✅ Índices compuestos con `__table_args__`

#### **Diseño de Base de Datos:**
✅ Referencias lógicas (int sin FK) para cross-database
✅ Foreign Keys solo dentro de la misma DB
✅ Desnormalización estratégica para histórico
✅ Auditoría completa (created_at, updated_at, created_by)
✅ Soft deletes con `is_active`
✅ JSON almacenado como TEXT (compatible)

#### **Funcionalidades Específicas:**
✅ Numeración única por sede (SEDE-AAAA-NNNNNN)
✅ Soporte para boletas y facturas electrónicas
✅ Reintentos automáticos (lab-sync, notifications)
✅ Conciliación diaria con detección de discrepancias
✅ Historial de cambios (precios, estados, auditoría)
✅ Plantillas de notificación dinámicas
✅ Backups con logs y metadata

---

### 📚 Próximos Pasos Recomendados

1. **Migrar modelos a cada microservicio:**
   - Copiar los modelos a `{servicio}/src/models/`
   - Actualizar imports según estructura de cada servicio

2. **Crear schemas Pydantic:**
   - Request DTOs (validación de entrada)
   - Response DTOs (serialización de salida)

3. **Implementar servicios (business logic):**
   - CRUD operations
   - Validaciones de negocio
   - Integración con otros servicios

4. **Generar migraciones Alembic:**
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

5. **Testing:**
   - Unit tests para modelos
   - Integration tests para relaciones

---

**Documento completado el 2025-10-31** ✅
#!/usr/bin/env python3
"""
Script automatizado para generar archivos de configuración y modelos
para todos los microservicios del sistema de laboratorio clínico.

Autor: Sistema Automatizado
Fecha: 2025-10-31
"""
import os
from pathlib import Path


# Configuración base de cada servicio
SERVICES_CONFIG = {
    "order-service": {
        "port": 8004,
        "database": "order_db",
        "db_port": 5435,
        "service_urls": {
            "PATIENT_SERVICE_URL": "http://localhost:8002",
            "CATALOG_SERVICE_URL": "http://localhost:8003",
            "USER_SERVICE_URL": "http://localhost:8001",
            "BILLING_SERVICE_URL": "http://localhost:8005",
            "NOTIFICATION_SERVICE_URL": "http://localhost:8006",
        },
        "has_security": False,
        "has_rabbitmq": True,
    },
    "laboratory-integration-service": {
        "port": 8008,
        "database": "order_db",  # SHARED
        "db_port": 5435,
        "service_urls": {
            "ORDER_SERVICE_URL": "http://localhost:8004",
            "PATIENT_SERVICE_URL": "http://localhost:8002",
        },
        "has_security": False,
        "has_rabbitmq": True,
    },
    "billing-service": {
        "port": 8005,
        "database": "billing_db",
        "db_port": 5436,
        "service_urls": {
            "ORDER_SERVICE_URL": "http://localhost:8004",
            "PATIENT_SERVICE_URL": "http://localhost:8002",
            "CONFIGURATION_SERVICE_URL": "http://localhost:8010",
            "NOTIFICATION_SERVICE_URL": "http://localhost:8006",
        },
        "has_security": False,
        "has_rabbitmq": True,
    },
    "reconciliation-service": {
        "port": 8007,
        "database": "billing_db",  # SHARED
        "db_port": 5436,
        "service_urls": {
            "ORDER_SERVICE_URL": "http://localhost:8004",
            "BILLING_SERVICE_URL": "http://localhost:8005",
            "NOTIFICATION_SERVICE_URL": "http://localhost:8006",
        },
        "has_security": False,
        "has_rabbitmq": False,
    },
    "configuration-service": {
        "port": 8010,
        "database": "config_db",
        "db_port": 5437,
        "service_urls": {},
        "has_security": False,
        "has_rabbitmq": False,
        "has_minio": True,
    },
    "notification-service": {
        "port": 8006,
        "database": "config_db",  # SHARED
        "db_port": 5437,
        "service_urls": {
            "CONFIGURATION_SERVICE_URL": "http://localhost:8010",
        },
        "has_security": False,
        "has_rabbitmq": True,
    },
    "reporting-service": {
        "port": 8009,
        "database": None,  # Redis only
        "db_port": None,
        "service_urls": {
            "ORDER_SERVICE_URL": "http://localhost:8004",
            "BILLING_SERVICE_URL": "http://localhost:8005",
            "PATIENT_SERVICE_URL": "http://localhost:8002",
            "CATALOG_SERVICE_URL": "http://localhost:8003",
            "RECONCILIATION_SERVICE_URL": "http://localhost:8007",
        },
        "has_security": False,
        "has_rabbitmq": False,
        "has_redis": True,
    },
}


def create_env_example(service_name: str, config: dict) -> str:
    """Genera contenido del archivo .env.example"""
    service_display = service_name.replace("-", " ").title().replace(" ", "")

    content = f"""# Service Configuration
SERVICE_NAME={service_name}
ENVIRONMENT=development
PORT={config['port']}

"""

    # Database
    if config['database']:
        shared_note = " (SHARED)" if config['database'] in ['order_db', 'billing_db', 'config_db'] else ""
        content += f"""# Database{shared_note}
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:{config['db_port']}/{config['database']}
DB_ECHO=false

"""
    elif config.get('has_redis'):
        content += """# Redis (No PostgreSQL - cache only)
REDIS_URL=redis://localhost:6379/0

"""

    # CORS
    content += """# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:8000"]

"""

    # Service URLs
    if config['service_urls']:
        content += "# Service URLs (for inter-service communication)\n"
        for key, value in config['service_urls'].items():
            content += f"{key}={value}\n"
        content += "\n"

    # RabbitMQ
    if config.get('has_rabbitmq'):
        content += """# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

"""

    # MinIO
    if config.get('has_minio'):
        content += """# MinIO (S3-compatible storage)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=lab-backups

"""

    # SMTP (for notification service)
    if service_name == "notification-service":
        content += """# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@laboratory.com
SMTP_FROM_NAME=Laboratory System

# WhatsApp API
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_TOKEN=your-whatsapp-token

"""

    # SUNAT (for billing service)
    if service_name == "billing-service":
        content += """# SUNAT/PSE Configuration
SUNAT_RUC=20123456789
SUNAT_USER=MODDATOS
SUNAT_PASSWORD=MODDATOS
SUNAT_ENDPOINT=https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService
SUNAT_ENVIRONMENT=TEST

"""

    # Logging
    content += """# Logging
LOG_LEVEL=INFO
"""

    return content


def create_config_py(service_name: str, config: dict) -> str:
    """Genera contenido del archivo config.py"""
    service_class = service_name.replace("-", " ").title().replace(" ", "")

    content = f'''"""
Service configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Settings for {service_name}"""

    # Service info
    service_name: str = Field(default="{service_name}", env="SERVICE_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default={config['port']}, env="PORT")

'''

    # Database
    if config['database']:
        content += '''    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_echo: bool = Field(default=False, env="DB_ECHO")

'''
    elif config.get('has_redis'):
        content += '''    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

'''

    # CORS
    content += '''    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

'''

    # Service URLs
    if config['service_urls']:
        content += "    # Service URLs\n"
        for key, value in config['service_urls'].items():
            default_val = value
            content += f'    {key.lower()}: str = Field(default="{default_val}", env="{key}")\n'
        content += "\n"

    # RabbitMQ
    if config.get('has_rabbitmq'):
        content += '''    # RabbitMQ
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/", env="RABBITMQ_URL")

'''

    # MinIO
    if config.get('has_minio'):
        content += '''    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    minio_bucket: str = Field(default="lab-backups", env="MINIO_BUCKET")

'''

    # SMTP
    if service_name == "notification-service":
        content += '''    # SMTP
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_from_email: str = Field(..., env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Laboratory System", env="SMTP_FROM_NAME")

    # WhatsApp
    whatsapp_api_url: str = Field(..., env="WHATSAPP_API_URL")
    whatsapp_api_token: str = Field(..., env="WHATSAPP_API_TOKEN")

'''

    # SUNAT
    if service_name == "billing-service":
        content += '''    # SUNAT
    sunat_ruc: str = Field(..., env="SUNAT_RUC")
    sunat_user: str = Field(..., env="SUNAT_USER")
    sunat_password: str = Field(..., env="SUNAT_PASSWORD")
    sunat_endpoint: str = Field(..., env="SUNAT_ENDPOINT")
    sunat_environment: str = Field(default="TEST", env="SUNAT_ENVIRONMENT")

'''

    # Logging
    content += '''    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton
settings = Settings()
'''

    return content


def create_database_py(service_name: str, config: dict) -> str:
    """Genera contenido del archivo database.py"""

    if not config['database']:
        # Redis only (reporting service)
        return '''"""
Redis configuration for reporting service
"""
import redis.asyncio as redis
from loguru import logger

from src.core.config import settings


# Redis client
redis_client = None


async def get_redis():
    """Get Redis client"""
    global redis_client

    if redis_client is None:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client

    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis connection closed")
'''

    return '''"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from src.core.config import settings


# Base para modelos SQLAlchemy
class Base(DeclarativeBase):
    pass


# Engine asíncrono
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """Dependency para obtener sesión de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise
'''


def get_model_content(service_name: str) -> tuple:
    """Retorna el contenido del modelo según el servicio"""

    models = {
        "order-service": {
            "filename": "order.py",
            "imports": "Order, OrderItem, OrderPayment, OrderDiscount, OrderStatusHistory, OrderStatus, PaymentMethod, DiscountType",
            "content": '''"""
Order Service Models
Database: order_db (COMPARTIDA con laboratory-integration-service)
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
    igv_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    igv_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Anulación
    cancelled_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
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

    # Datos desnormalizados
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
    """Métodos de pago de una orden"""
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
    registered_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<OrderPayment(order_id={self.order_id}, method={self.payment_method}, amount={self.amount})>"


class OrderDiscount(Base):
    """Descuentos aplicados a una orden"""
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
    applied_by: Mapped[int] = mapped_column(Integer, nullable=False)
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
    changed_by: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="status_history")

    def __repr__(self):
        return f"<OrderStatusHistory(order_id={self.order_id}, {self.old_status} -> {self.new_status})>"
'''
        },
        "laboratory-integration-service": {
            "filename": "lab_sync.py",
            "imports": "LabSyncLog, SyncStatus",
            "content": '''"""
Laboratory Integration Service Models
Database: order_db (COMPARTIDA con order-service)
Owner: laboratory-integration-service
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
    request_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    response_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as TEXT
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<LabSyncLog(id={self.id}, order_id={self.order_id}, status={self.sync_status}, attempts={self.attempt_count})>"
'''
        },
        # Continuará con los demás servicios...
    }

    if service_name in models:
        return models[service_name]["filename"], models[service_name]["imports"], models[service_name]["content"]

    return None, None, None


def generate_service_files(base_path: Path):
    """Genera todos los archivos para todos los servicios"""

    print("🚀 Iniciando generación automatizada de servicios...")
    print(f"📁 Ruta base: {base_path}\n")

    for service_name, config in SERVICES_CONFIG.items():
        print(f"⚙️  Procesando {service_name}...")

        service_path = base_path / service_name
        src_path = service_path / "src"
        core_path = src_path / "core"
        models_path = src_path / "models"

        # Crear directorios si no existen
        core_path.mkdir(parents=True, exist_ok=True)
        models_path.mkdir(parents=True, exist_ok=True)

        # 1. .env.example
        env_file = service_path / ".env.example"
        if not env_file.exists():
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(create_env_example(service_name, config))
            print(f"   ✅ {env_file.name}")
        else:
            print(f"   ⏭️  {env_file.name} (ya existe)")

        # 2. src/__init__.py
        src_init = src_path / "__init__.py"
        if not src_init.exists():
            with open(src_init, 'w', encoding='utf-8') as f:
                f.write(f'"""\n{service_name.replace("-", " ").title()}\n"""\n')
            print(f"   ✅ src/__init__.py")

        # 3. src/core/__init__.py
        core_init = core_path / "__init__.py"
        if not core_init.exists():
            with open(core_init, 'w', encoding='utf-8') as f:
                f.write('"""\nCore module\n"""\n')
            print(f"   ✅ src/core/__init__.py")

        # 4. src/core/config.py
        config_file = core_path / "config.py"
        if not config_file.exists():
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(create_config_py(service_name, config))
            print(f"   ✅ src/core/config.py")
        else:
            print(f"   ⏭️  src/core/config.py (ya existe)")

        # 5. src/core/database.py
        db_file = core_path / "database.py"
        if not db_file.exists():
            with open(db_file, 'w', encoding='utf-8') as f:
                f.write(create_database_py(service_name, config))
            print(f"   ✅ src/core/database.py")
        else:
            print(f"   ⏭️  src/core/database.py (ya existe)")

        # 6. src/models/__init__.py y modelos
        model_filename, model_imports, model_content = get_model_content(service_name)

        if model_filename and model_content:
            # models/__init__.py
            models_init = models_path / "__init__.py"
            if not models_init.exists():
                with open(models_init, 'w', encoding='utf-8') as f:
                    module_name = model_filename.replace('.py', '')
                    f.write(f'"""\n{service_name.replace("-", " ").title()} Models\n"""\n')
                    f.write(f'from src.models.{module_name} import {model_imports}\n\n')
                    imports_list = [f'"{m.strip()}"' for m in model_imports.split(",")]
                    f.write(f'__all__ = [{", ".join(imports_list)}]\n')
                print(f"   ✅ src/models/__init__.py")

            # model file
            model_file = models_path / model_filename
            if not model_file.exists():
                with open(model_file, 'w', encoding='utf-8') as f:
                    f.write(model_content)
                print(f"   ✅ src/models/{model_filename}")
            else:
                print(f"   ⏭️  src/models/{model_filename} (ya existe)")

        print(f"   ✅ {service_name} completado!\n")

    print("🎉 Generación completada exitosamente!")
    print("\n📋 Resumen:")
    print(f"   - Servicios procesados: {len(SERVICES_CONFIG)}")
    print(f"   - Archivos generados por servicio: ~6")
    print(f"   - Total estimado: ~{len(SERVICES_CONFIG) * 6} archivos")


if __name__ == "__main__":
    # Obtener directorio base (LabMicroServ)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    print(f"Script ejecutándose desde: {script_dir}")
    print(f"Directorio base del proyecto: {base_dir}\n")

    # Confirmar antes de proceder
    response = input("¿Deseas continuar con la generación? (s/n): ")

    if response.lower() == 's':
        generate_service_files(base_dir)
    else:
        print("❌ Generación cancelada por el usuario")

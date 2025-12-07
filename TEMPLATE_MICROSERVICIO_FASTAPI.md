# 🚀 Template Definitivo: Microservicio FastAPI

Este template sigue las **mejores prácticas 2024** para microservicios con FastAPI, basado en la arquitectura GeoAttend.

---

## 📁 Estructura del Microservicio

```
nombre-servicio/
├── Dockerfile
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app + lifespan
│   │
│   ├── core/                      # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py              # Settings con pydantic-settings
│   │   ├── database.py            # AsyncSession + create_tables()
│   │   └── security.py            # JWT utilities (si aplica)
│   │
│   ├── models/                    # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   └── entidad.py
│   │
│   ├── schemas/                   # Pydantic v2 validation
│   │   ├── __init__.py
│   │   ├── requests.py            # DTOs de entrada
│   │   └── responses.py           # DTOs de salida
│   │
│   ├── repositories/              # Data access layer (CRUD operations)
│   │   ├── __init__.py
│   │   └── entidad.py             # Solo operaciones de BD
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── entidad_service.py     # Validaciones y orquestación
│   │   └── http_client.py         # Cliente HTTP para otros servicios
│   │
│   ├── routers/                   # Endpoints REST
│   │   ├── __init__.py
│   │   ├── entidad.py
│   │   └── health.py              # Health checks
│   │
│   ├── utils/                     # Utilidades (opcional)
│   │   ├── __init__.py
│   │   └── helpers.py
│   │
│   ├── dependencies.py            # FastAPI dependencies
│   └── exceptions.py              # Excepciones personalizadas
│
└── tests/                         # Testing
    ├── __init__.py
    ├── conftest.py
    ├── test_endpoints.py
    └── test_services.py
```

---

## 🔧 Archivos Base

### 1️⃣ `requirements.txt`

```txt
# FastAPI & Server
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0

# Validation & Config
pydantic==2.9.0
pydantic-settings==2.5.0

# Security (si aplica)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# HTTP Client (para comunicación inter-servicios)
httpx==0.27.0

# Logging
loguru==0.7.2

# Utils
python-dotenv==1.0.0

# Testing
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0
```

---

### 2️⃣ `Dockerfile`

```dockerfile
# Multi-stage build para optimización
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa final
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=builder /root/.local /root/.local

# Copiar código fuente
COPY src/ ./src/

# Crear usuario sin privilegios
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

# Variables de entorno por defecto
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Exponer puerto (cambiar según servicio)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3️⃣ `src/main.py` - FastAPI Application

```python
"""
Main FastAPI application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from src.core.config import settings
from src.core.database import create_tables
from src.routers import health, entidad  # Importar tus routers

# Configurar logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown"""
    # Startup
    logger.info(f"🚀 Starting {settings.service_name} on port {settings.port}")
    logger.info(f"📦 Environment: {settings.environment}")

    # Crear tablas si no existen
    await create_tables()
    logger.info("✅ Database tables created/verified")

    yield

    # Shutdown
    logger.info(f"🛑 Shutting down {settings.service_name}")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.service_name,
    description=f"API for {settings.service_name}",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, tags=["Health"])
app.include_router(entidad.router, prefix="/api", tags=["Entidad"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "running"
    }
```

---

### 4️⃣ `src/core/config.py` - Configuration

```python
"""
Service configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Settings for the service"""

    # Service info
    service_name: str = "nombre-servicio"
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default=8000, env="PORT")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_echo: bool = Field(default=False, env="DB_ECHO")

    # Security (si aplica)
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )

    # Service URLs (para comunicación inter-servicios)
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    course_service_url: str = Field(default="http://localhost:8002", env="COURSE_SERVICE_URL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton
settings = Settings()
```

---

### 5️⃣ `src/core/database.py` - Database Connection

```python
"""
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
```

---

### 6️⃣ `src/core/security.py` - Security (si aplica)

```python
"""
Security utilities for JWT authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from loguru import logger

from src.core.config import settings


# Context para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

---

### 7️⃣ `src/models/entidad.py` - SQLAlchemy Model

```python
"""
Database model for Entidad
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.core.database import Base


class Entidad(Base):
    """SQLAlchemy model for Entidad"""

    __tablename__ = "entidades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Entidad(id={self.id}, nombre='{self.nombre}')>"
```

---

### 8️⃣ `src/schemas/requests.py` - Request DTOs

```python
"""
Pydantic schemas for request validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class EntidadCreateRequest(BaseModel):
    """Schema for creating a new Entidad"""

    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre de la entidad")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional")
    activo: bool = Field(default=True, description="Estado activo/inactivo")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Ejemplo Entidad",
                "descripcion": "Esta es una entidad de ejemplo",
                "activo": True
            }
        }
    )


class EntidadUpdateRequest(BaseModel):
    """Schema for updating an existing Entidad"""

    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=500)
    activo: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Entidad Actualizada",
                "descripcion": "Descripción modificada",
                "activo": False
            }
        }
    )
```

---

### 9️⃣ `src/schemas/responses.py` - Response DTOs

```python
"""
Pydantic schemas for API responses
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Any


class EntidadResponse(BaseModel):
    """Schema for Entidad response"""

    id: int
    nombre: str
    descripcion: Optional[str]
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "OK"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }
    )


class DataResponse(BaseResponse):
    """Response with data payload"""
    data: Any

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": {"id": 1, "nombre": "Ejemplo"}
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    details: Optional[dict] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Resource not found",
                "details": {"resource_id": 123}
            }
        }
    )


class PaginatedResponse(BaseResponse):
    """Paginated response schema"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
```

---

### 🔟 `src/services/entidad_service.py` - Business Logic

```python
"""
Business logic for Entidad operations
"""
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from loguru import logger

from src.models.entidad import Entidad
from src.schemas.requests import EntidadCreateRequest, EntidadUpdateRequest
from src.exceptions import EntityNotFoundError


class EntidadService:
    """Service class for Entidad business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, entidad_data: EntidadCreateRequest) -> Entidad:
        """Create a new Entidad"""
        try:
            new_entidad = Entidad(**entidad_data.model_dump())
            self.db.add(new_entidad)
            await self.db.commit()
            await self.db.refresh(new_entidad)

            logger.info(f"✅ Entidad created: id={new_entidad.id}, nombre={new_entidad.nombre}")
            return new_entidad

        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating Entidad: {e}")
            raise

    async def get_by_id(self, entidad_id: int) -> Optional[Entidad]:
        """Get Entidad by ID"""
        try:
            result = await self.db.execute(
                select(Entidad).where(Entidad.id == entidad_id)
            )
            entidad = result.scalar_one_or_none()

            if not entidad:
                logger.warning(f"⚠️ Entidad not found: id={entidad_id}")
                raise EntityNotFoundError(f"Entidad with id {entidad_id} not found")

            return entidad

        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching Entidad: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100, activo: Optional[bool] = None) -> List[Entidad]:
        """Get all Entidades with pagination"""
        try:
            query = select(Entidad)

            if activo is not None:
                query = query.where(Entidad.activo == activo)

            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            entidades = result.scalars().all()

            logger.info(f"📋 Retrieved {len(entidades)} entidades")
            return list(entidades)

        except Exception as e:
            logger.error(f"❌ Error fetching Entidades: {e}")
            raise

    async def update(self, entidad_id: int, entidad_data: EntidadUpdateRequest) -> Entidad:
        """Update an existing Entidad"""
        try:
            # Verificar que existe
            entidad = await self.get_by_id(entidad_id)

            # Actualizar solo campos no-None
            update_data = entidad_data.model_dump(exclude_unset=True)

            if update_data:
                await self.db.execute(
                    update(Entidad)
                    .where(Entidad.id == entidad_id)
                    .values(**update_data)
                )
                await self.db.commit()
                await self.db.refresh(entidad)

            logger.info(f"✅ Entidad updated: id={entidad_id}")
            return entidad

        except EntityNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error updating Entidad: {e}")
            raise

    async def delete(self, entidad_id: int) -> bool:
        """Delete an Entidad"""
        try:
            # Verificar que existe
            await self.get_by_id(entidad_id)

            await self.db.execute(
                delete(Entidad).where(Entidad.id == entidad_id)
            )
            await self.db.commit()

            logger.info(f"🗑️ Entidad deleted: id={entidad_id}")
            return True

        except EntityNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error deleting Entidad: {e}")
            raise
```

---

### 1️⃣1️⃣ `src/services/http_client.py` - HTTP Client para Comunicación Inter-Servicios

```python
"""
HTTP Client for inter-service communication
"""
import httpx
from typing import Optional, Dict, Any
from loguru import logger


class ServiceClient:
    """HTTP client for communicating with other microservices"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make GET request to another service"""
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()

            logger.info(f"✅ GET {self.base_url}{endpoint} - Status: {response.status_code}")
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return None

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make POST request to another service"""
        try:
            response = await self.client.post(endpoint, json=json_data)
            response.raise_for_status()

            logger.info(f"✅ POST {self.base_url}{endpoint} - Status: {response.status_code}")
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
```

---

### 1️⃣2️⃣ `src/routers/entidad.py` - API Endpoints

```python
"""
API endpoints for Entidad resource
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from loguru import logger

from src.core.database import get_db
from src.services.entidad_service import EntidadService
from src.schemas.requests import EntidadCreateRequest, EntidadUpdateRequest
from src.schemas.responses import EntidadResponse, DataResponse, ErrorResponse
from src.exceptions import EntityNotFoundError


router = APIRouter(prefix="/entidades")


@router.post(
    "/",
    response_model=DataResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Entidad created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"}
    }
)
async def create_entidad(
    entidad_data: EntidadCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new Entidad"""
    try:
        service = EntidadService(db)
        entidad = await service.create(entidad_data)

        return DataResponse(
            success=True,
            message="Entidad created successfully",
            data=EntidadResponse.model_validate(entidad)
        )

    except Exception as e:
        logger.error(f"❌ Error creating Entidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{entidad_id}",
    response_model=DataResponse,
    responses={
        200: {"description": "Entidad retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Entidad not found"}
    }
)
async def get_entidad(
    entidad_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get Entidad by ID"""
    try:
        service = EntidadService(db)
        entidad = await service.get_by_id(entidad_id)

        return DataResponse(
            success=True,
            message="Entidad retrieved successfully",
            data=EntidadResponse.model_validate(entidad)
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving Entidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=DataResponse,
    responses={
        200: {"description": "Entidades retrieved successfully"}
    }
)
async def list_entidades(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    activo: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """List all Entidades with pagination"""
    try:
        service = EntidadService(db)
        entidades = await service.get_all(skip=skip, limit=limit, activo=activo)

        return DataResponse(
            success=True,
            message=f"Retrieved {len(entidades)} entidades",
            data=[EntidadResponse.model_validate(e) for e in entidades]
        )

    except Exception as e:
        logger.error(f"❌ Error listing Entidades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{entidad_id}",
    response_model=DataResponse,
    responses={
        200: {"description": "Entidad updated successfully"},
        404: {"model": ErrorResponse, "description": "Entidad not found"}
    }
)
async def update_entidad(
    entidad_id: int,
    entidad_data: EntidadUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing Entidad"""
    try:
        service = EntidadService(db)
        entidad = await service.update(entidad_id, entidad_data)

        return DataResponse(
            success=True,
            message="Entidad updated successfully",
            data=EntidadResponse.model_validate(entidad)
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error updating Entidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{entidad_id}",
    response_model=DataResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Entidad deleted successfully"},
        404: {"model": ErrorResponse, "description": "Entidad not found"}
    }
)
async def delete_entidad(
    entidad_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an Entidad"""
    try:
        service = EntidadService(db)
        await service.delete(entidad_id)

        return DataResponse(
            success=True,
            message="Entidad deleted successfully",
            data={"id": entidad_id}
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error deleting Entidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

---

### 1️⃣3️⃣ `src/routers/health.py` - Health Check

```python
"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from loguru import logger

from src.core.database import get_db
from src.core.config import settings


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    Returns service status and database connectivity
    """
    try:
        # Check database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result else "unhealthy"

        return {
            "service": settings.service_name,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "environment": settings.environment
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "service": settings.service_name,
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "unhealthy",
            "error": str(e)
        }


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check for Kubernetes/container orchestration
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get("/liveness")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration
    """
    return {"alive": True}
```

---

### 1️⃣4️⃣ `src/dependencies.py` - FastAPI Dependencies

```python
"""
FastAPI dependency injection functions
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.core.security import decode_access_token
from src.services.entidad_service import EntidadService


security = HTTPBearer()


async def get_entidad_service(db: AsyncSession = Depends(get_db)) -> EntidadService:
    """Dependency to get EntidadService instance"""
    return EntidadService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    Use this if your service requires authentication
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id: Optional[int] = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency to ensure user is active"""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
```

---

### 1️⃣5️⃣ `src/exceptions.py` - Custom Exceptions

```python
"""
Custom exception classes
"""


class ServiceException(Exception):
    """Base exception for service errors"""
    pass


class EntityNotFoundError(ServiceException):
    """Raised when an entity is not found in the database"""
    pass


class ValidationError(ServiceException):
    """Raised when validation fails"""
    pass


class AuthenticationError(ServiceException):
    """Raised when authentication fails"""
    pass


class AuthorizationError(ServiceException):
    """Raised when user lacks permissions"""
    pass
```

---

### 1️⃣6️⃣ `.env.example` - Environment Variables Template

```env
# Service Configuration
SERVICE_NAME=nombre-servicio
ENVIRONMENT=development
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DB_ECHO=false

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Service URLs (for inter-service communication)
USER_SERVICE_URL=http://localhost:8001
COURSE_SERVICE_URL=http://localhost:8002
ATTENDANCE_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8004

# Logging
LOG_LEVEL=INFO
```

---

### 1️⃣7️⃣ `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

---

### 1️⃣8️⃣ `README.md` - Service Documentation

```markdown
# Nombre del Microservicio

Descripción breve del propósito del microservicio.

## 🚀 Características

- FastAPI con Python 3.11
- SQLAlchemy 2.0 (Async)
- PostgreSQL
- JWT Authentication
- Docker ready
- Health checks

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 14+
- Docker (opcional)

## ⚙️ Instalación

### Local (sin Docker)

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar el servicio:
```bash
uvicorn src.main:app --reload --port 8000
```

### Con Docker

```bash
docker build -t nombre-servicio .
docker run -p 8000:8000 --env-file .env nombre-servicio
```

## 📚 API Documentation

Una vez ejecutado el servicio, accede a:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```bash
pytest tests/ -v
```

## 🏗️ Estructura

```
nombre-servicio/
├── src/
│   ├── core/          # Configuración y utilidades centrales
│   ├── models/        # Modelos SQLAlchemy
│   ├── schemas/       # Esquemas Pydantic
│   ├── services/      # Lógica de negocio
│   └── routers/       # Endpoints API
├── tests/             # Tests
├── Dockerfile
└── requirements.txt
```

## 🔗 Endpoints Principales

- `GET /health` - Health check
- `GET /api/entidades` - Listar entidades
- `POST /api/entidades` - Crear entidad
- `GET /api/entidades/{id}` - Obtener entidad
- `PUT /api/entidades/{id}` - Actualizar entidad
- `DELETE /api/entidades/{id}` - Eliminar entidad

## 🔐 Seguridad

Este servicio utiliza JWT para autenticación. Incluye el token en el header:
```
Authorization: Bearer <token>
```

## 📝 Licencia

[Tu licencia aquí]
```

---

## 🎯 Instrucciones de Uso

### Para crear un nuevo microservicio:

1. **Copiar estructura completa**
2. **Renombrar "entidad" por tu recurso** (ej: "product", "order", "invoice")
3. **Actualizar configuración**:
   - `.env.example` con tus variables
   - `src/core/config.py` con settings específicas
   - `Dockerfile` con el puerto correcto
4. **Definir tu modelo** en `src/models/`
5. **Crear schemas** en `src/schemas/`
6. **Implementar lógica** en `src/services/`
7. **Crear endpoints** en `src/routers/`

### Ejemplo de uso rápido:

```bash
# 1. Crear directorio
mkdir product-service
cd product-service

# 2. Copiar archivos del template

# 3. Crear .env
cp .env.example .env

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
uvicorn src.main:app --reload --port 8005
```

---

## ✅ Checklist de Implementación

- [ ] Estructura de carpetas creada
- [ ] `requirements.txt` configurado
- [ ] `Dockerfile` ajustado al puerto correcto
- [ ] `.env` configurado con credenciales reales
- [ ] Modelos SQLAlchemy definidos
- [ ] Schemas Pydantic creados
- [ ] Service layer implementado
- [ ] Routers con endpoints REST
- [ ] Health checks funcionando
- [ ] Logging configurado
- [ ] Tests unitarios escritos
- [ ] README.md documentado
- [ ] Docker image construida
- [ ] Integración con otros servicios testeada

---

## 🔗 Integración con Docker Compose

Agregar al `docker-compose.yml` raíz:

```yaml
nombre-servicio:
  build: ./nombre-servicio
  container_name: nombre-servicio
  ports:
    - "8005:8005"
  environment:
    - DATABASE_URL=postgresql+asyncpg://user:pass@nombre_db:5432/nombre_db
    - SECRET_KEY=${SECRET_KEY}
  depends_on:
    - nombre_db
  networks:
    - app-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8005/health"]
    interval: 30s
    timeout: 10s
    retries: 3

nombre_db:
  image: postgres:14-alpine
  container_name: nombre_db
  environment:
    POSTGRES_DB: nombre_db
    POSTGRES_USER: user
    POSTGRES_PASSWORD: pass
  ports:
    - "5437:5432"
  volumes:
    - nombre_db_data:/var/lib/postgresql/data
  networks:
    - app-network

volumes:
  nombre_db_data:

networks:
  app-network:
    driver: bridge
```

---

## 🎓 Buenas Prácticas Aplicadas

✅ **Arquitectura limpia** con separación de capas
✅ **Async/Await** para operaciones I/O
✅ **Dependency Injection** con FastAPI
✅ **Validación** con Pydantic v2
✅ **ORM Async** con SQLAlchemy 2.0
✅ **Logging estructurado** con Loguru
✅ **Health checks** para monitoreo
✅ **Security** con JWT y bcrypt
✅ **Docker** multi-stage builds
✅ **Type hints** en todo el código
✅ **Error handling** consistente
✅ **HTTP client** para comunicación inter-servicios

---

**🚀 ¡Template listo para producción siguiendo las mejores prácticas de microservicios FastAPI 2024!**

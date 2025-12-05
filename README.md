# 🏥 Sistema de Microservicios - Laboratorio Clínico

Sistema de gestión integral para laboratorio clínico basado en arquitectura de microservicios con FastAPI, PostgreSQL y Docker.

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Setup](#instalación-y-setup)
- [Estado del Proyecto](#estado-del-proyecto)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Servicios](#servicios)
- [Bases de Datos](#bases-de-datos)
- [Autenticación](#autenticación)
- [Desarrollo](#desarrollo)
- [Testing](#testing)
- [Documentación](#documentación)

## 🏗️ Arquitectura

El sistema está compuesto por 6 microservicios independientes + API Gateway:

```
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY (8000)                      │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  User Service   │  │ Patient Service │  │ Order Service  │
│   (Port 8001)   │  │   (Port 8002)   │  │  (Port 8003)   │
│    user_db      │  │   patient_db    │  │   order_db     │
└─────────────────┘  └─────────────────┘  └────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│ Billing Service │  │  Config Service │  │Reporting Service│
│   (Port 8004)   │  │   (Port 8005)   │  │  (Port 8006)   │
│   billing_db    │  │    config_db    │  │   (Analytics)  │
└─────────────────┘  └─────────────────┘  └────────────────┘
```

## 🛠️ Tecnologías

- **Backend:** FastAPI 0.104+, Python 3.11+
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 15
- **Authentication:** JWT (python-jose) + bcrypt
- **Containers:** Docker, Docker Compose
- **Migrations:** Alembic
- **Logging:** Loguru
- **Validation:** Pydantic 2.5+
- **Testing:** Pytest

## 📦 Requisitos Previos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Python** >= 3.11 (para desarrollo local sin Docker)
- **Git**

## 🚀 Instalación y Setup

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd LabMicroServ
```

### 2. Levantar los servicios con Docker Compose

```bash
# Levantar todos los servicios (bases de datos + microservicios)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f user-service
```

### 3. Ejecutar migraciones de base de datos

```bash
# User Service
docker-compose exec user-service alembic upgrade head

# Patient Service
docker-compose exec patient-service alembic upgrade head

# Order Service
docker-compose exec order-service alembic upgrade head

# Billing Service
docker-compose exec billing-service alembic upgrade head

# Configuration Service
docker-compose exec configuration-service alembic upgrade head
```

### 4. Poblar datos iniciales (Seed)

```bash
# Crear roles y usuario administrador
docker-compose exec user-service python seed_data.py
```

**Credenciales del administrador:**
- Email: `admin@labclinico.com`
- Password: `Admin123`

⚠️ **IMPORTANTE:** Cambia la contraseña del admin después del primer login.

### 5. Verificar que los servicios estén corriendo

```bash
# Health checks
curl http://localhost:8001/health  # User Service
curl http://localhost:8002/health  # Patient Service
curl http://localhost:8003/health  # Order Service
curl http://localhost:8004/health  # Billing Service
curl http://localhost:8005/health  # Configuration Service
```

### 6. Acceder a la documentación API (Swagger UI)

- **User Service:** http://localhost:8001/docs
- **Patient Service:** http://localhost:8002/docs
- **Order Service:** http://localhost:8003/docs
- **Billing Service:** http://localhost:8004/docs
- **Configuration Service:** http://localhost:8005/docs
- **API Gateway:** http://localhost:8000/docs

## 🚦 Estado del Proyecto

**Sprint Actual:** Sprint 1 (18 nov - 24 nov)

### ✅ Completado

#### Infrastructure
- ✅ Docker Compose configurado (6 servicios + 5 bases de datos)
- ✅ Alembic configurado en todos los servicios
- ✅ Migraciones iniciales aplicadas
- ✅ Variables de entorno (.env) configuradas

#### F-30: Configuración General (Configuration Service)
- ✅ Modelos: CompanyInfo, Location, SystemSetting
- ✅ CRUD completo para información de empresa
- ✅ CRUD completo para sedes/sucursales
- ✅ CRUD completo para configuraciones del sistema
- ✅ 15 endpoints REST documentados
- ✅ Validaciones de negocio implementadas

#### F-01: Autenticación de Usuarios (User Service)
- ✅ Modelos: User, Role, UserRole, PasswordResetToken, AuditLog
- ✅ Sistema de autenticación JWT
- ✅ Login con email/password
- ✅ Registro de usuarios con roles
- ✅ Cambio de contraseña
- ✅ Recuperación de contraseña (reset tokens)
- ✅ Middleware de autenticación
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Auditoría de acciones (login, registro, cambios)
- ✅ 8 endpoints REST documentados
- ✅ Seed data: 4 roles + usuario admin

**Roles disponibles:**
1. Administrador General (acceso completo)
2. Recepcionista (pacientes, órdenes, facturación)
3. Supervisor de Sede (reportes, conciliación)
4. Laboratorista (resultados de lab)

### 🔄 En Progreso
- ⏳ (Sprint 2) Gestión de pacientes completa

### 📋 Pendiente (Sprint 1)
✅ **¡SPRINT 1 COMPLETADO!**

### ✅ Recién Completado (Sprint 1)
- ✅ F-12: Control económico de órdenes
  - ✅ Registro de pagos por orden.
  - ✅ Cálculo de saldo pendiente.
- ✅ F-13: Control administrativo de órdenes
  - ✅ Gestión del ciclo de vida de la orden (Pendiente -> En Proceso -> Completada/Cancelada).
- ✅ F-11: Creación y gestión de órdenes
  - ✅ Creación de órdenes con múltiples pruebas del catálogo.
  - ✅ Cálculo automático de totales.
  - ✅ CRUD básico para órdenes y visualización de sus items.
- ✅ F-08, F-09, F-10: Módulo de Catálogo de Servicios
  - ✅ CRUD completo para Categorías, Tipos de Muestra y Pruebas de Laboratorio.
  - ✅ Gestión de precios y costos.
  - ✅ Búsqueda y filtrado avanzado de pruebas.
  - ✅ 15 nuevos endpoints REST documentados en `order-service`.
- ✅ F-02: Gestión de roles y permisos
  - ✅ CRUD completo para Usuarios
  - ✅ CRUD completo para Roles
  - ✅ Asignación y revocación de roles a usuarios
  - ✅ 12 nuevos endpoints REST documentados
- ✅ F-27: Reportes operativos básicos
  - ✅ Endpoint de resumen de órdenes (total, por estado, ingresos).

## 📁 Estructura del Proyecto

```
LabMicroServ/
├── docker-compose.yml          # Orquestación de servicios
├── .gitignore                  # Archivos ignorados
├── README.md                   # Este archivo
├── Sprint1.md                  # Planning Sprint 1
├── Historias.md                # User Stories
│
├── user-service/               # ✅ COMPLETADO
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── alembic.ini
│   ├── seed_data.py           # Script de datos iniciales
│   ├── alembic/               # Migraciones DB
│   │   └── versions/
│   └── src/
│       ├── main.py            # Entry point
│       ├── core/
│       │   ├── config.py      # Configuración
│       │   ├── database.py    # Conexión DB
│       │   └── security.py    # JWT, hashing, RBAC
│       ├── models/
│       │   └── user.py        # User, Role, UserRole, etc.
│       ├── schemas/
│       │   └── auth.py        # Pydantic schemas
│       ├── repositories/
│       │   └── auth.py        # Data access layer
│       ├── services/
│       │   └── auth.py        # Business logic
│       └── routers/
│           └── auth.py        # API endpoints
│
├── patient-service/            # 🔧 PREPARADO
│   ├── alembic/               # Migraciones aplicadas
│   └── src/
│       ├── models/            # PatientInfo, ContactInfo, etc.
│       └── ...
│
├── order-service/              # 🔧 PREPARADO (estructura modular)
│   ├── alembic/
│   └── src/
│       └── modules/
│           ├── catalog/       # Catálogo de servicios
│           ├── orders/        # Órdenes de servicio
│           └── lab_integration/ # Integración LIS
│
├── billing-service/            # 🔧 PREPARADO (estructura modular)
│   ├── alembic/
│   └── src/
│       └── modules/
│           ├── billing/       # Facturación SUNAT
│           └── reconciliation/ # Conciliación diaria
│
├── configuration-service/      # ✅ COMPLETADO (estructura modular)
│   ├── alembic/
│   └── src/
│       ├── main.py
│       └── modules/
│           ├── configuration/ # ✅ Config, Locations, Settings
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── repository.py
│           │   ├── service.py
│           │   └── router.py
│           └── notifications/ # 🔧 PREPARADO
│
├── api-gateway/                # 🔧 PREPARADO
│   └── src/
│       └── main.py
│
└── docs/                       # Documentación
    ├── ARQUITECTURA_MICROSERVICIOS.md
    ├── MODELOS_SQLALCHEMY.md
    └── Requirements.md
```

## 🎯 Servicios

### 1. User Service (Port 8001) ✅
**Estado:** Funcional

**Funcionalidades:**
- ✅ Login con JWT
- ✅ Registro de usuarios
- ✅ Gestión de roles (4 roles predefinidos)
- ✅ Cambio de contraseña
- ✅ Recuperación de contraseña
- ✅ Auditoría de acciones
- ✅ Control de acceso basado en roles

**Endpoints disponibles:** 8
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `GET /api/v1/auth/me` - Usuario actual
- `POST /api/v1/auth/change-password` - Cambiar contraseña
- `POST /api/v1/auth/request-password-reset` - Solicitar reset
- `POST /api/v1/auth/reset-password` - Restablecer contraseña
- `POST /api/v1/auth/verify-token` - Verificar token
- *(más endpoints pendientes para gestión de usuarios)*

**Base de datos:** `user_db` (5 tablas)

### 2. Patient Service (Port 8002) 🔧
**Estado:** Base de datos configurada, pendiente implementación

**Funcionalidades pendientes:**
- Registro y gestión de pacientes
- Historial clínico
- Validaciones de DNI/RUC
- Pacientes recurrentes

**Base de datos:** `patient_db` (3 tablas)

### 3. Order Service (Port 8003) 🔧
**Estado:** Base de datos configurada, pendiente implementación

**Módulos:**
- **Catalog:** Catálogo de servicios/exámenes
- **Orders:** Gestión de órdenes de servicio
- **Lab Integration:** Sincronización con LIS

**Endpoints disponibles (Catalog):** 15
- `GET /api/v1/catalog/tests` - Listar/buscar pruebas
- `POST /api/v1/catalog/tests` - Crear prueba
- `GET /api/v1/catalog/tests/{test_id}` - Obtener prueba
- `PUT /api/v1/catalog/tests/{test_id}` - Actualizar prueba
- `DELETE /api/v1/catalog/tests/{test_id}` - Desactivar prueba
- `GET /api/v1/catalog/categories` - Listar categorías
- `POST /api/v1/catalog/categories` - Crear categoría
- `PUT /api/v1/catalog/categories/{category_id}` - Actualizar categoría
- `GET /api/v1/catalog/sample-types` - Listar tipos de muestra
- `POST /api/v1/catalog/sample-types` - Crear tipo de muestra
- `PUT /api/v1/catalog/sample-types/{sample_type_id}` - Actualizar tipo de muestra

**Endpoints disponibles (Orders):** 5
- `POST /api/v1/orders` - Crear nueva orden
- `GET /api/v1/orders` - Listar órdenes
- `GET /api/v1/orders/{order_id}` - Obtener orden por ID
- `PUT /api/v1/orders/{order_id}` - Actualizar orden (datos básicos)
- `DELETE /api/v1/orders/{order_id}` - Cancelar orden
- `PUT /api/v1/orders/{order_id}/status` - Cambiar estado de la orden
- `POST /api/v1/orders/{order_id}/payments` - Registrar pago

**Endpoints disponibles (Reports):** 1
- `GET /api/v1/reports/orders-summary` - Resumen de órdenes

**Base de datos:** `order_db` (9 tablas)

### 4. Billing Service (Port 8004) 🔧
**Estado:** Base de datos configurada, pendiente implementación

**Módulos:**
- **Billing:** Facturación electrónica SUNAT
- **Reconciliation:** Conciliación y cierre de caja

**Base de datos:** `billing_db` (4 tablas)

### 5. Configuration Service (Port 8005) ✅
**Estado:** Funcional

**Funcionalidades:**
- ✅ Gestión de información de empresa (RUC, razón social)
- ✅ Gestión de sedes/sucursales
- ✅ Configuración de parámetros del sistema (key-value)
- ✅ Actualización masiva de configuraciones

**Endpoints disponibles:** 15
- Información de empresa (3 endpoints)
- Sedes/Locations (5 endpoints)
- Configuraciones del sistema (7 endpoints)

**Base de datos:** `config_db` (5 tablas)

### 6. Reporting Service (Port 8006) 🔧
**Estado:** Pendiente implementación

**Funcionalidades pendientes:**
- Dashboard y KPIs
- Reportes operativos
- Data Warehouse
- Exportación a Excel/PDF

### 7. API Gateway (Port 8000) 🔧
**Estado:** Configurado, pendiente routing

**Funcionalidades pendientes:**
- Enrutamiento unificado
- Autenticación centralizada
- Rate limiting

## 🗄️ Bases de Datos

| Base de Datos | Puerto | Servicio | Tablas | Estado |
|---------------|--------|----------|--------|--------|
| `user_db` | 5432 | user-service | 5 | ✅ Migrado |
| `patient_db` | 5433 | patient-service | 3 | ✅ Migrado |
| `order_db` | 5434 | order-service | 9 | ✅ Migrado |
| `billing_db` | 5435 | billing-service | 4 | ✅ Migrado |
| `config_db` | 5436 | configuration-service | 5 | ✅ Migrado |

### Credenciales por defecto (Development):

```
Usuario: postgres
Password: 1234
```

**⚠️ CAMBIAR EN PRODUCCIÓN**

## 🔐 Autenticación

### Login

```bash
POST http://localhost:8001/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@labclinico.com",
  "password": "Admin123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@labclinico.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "roles": ["Administrador General"],
    "is_active": true
  }
}
```

### Usar el token en requests

```bash
Authorization: Bearer <access_token>
```

En Swagger UI:
1. Click en "Authorize" 🔒
2. Pegar: `Bearer <tu_token>`
3. Click "Authorize"

## 💻 Desarrollo

### Desarrollo local (sin Docker)

```bash
# 1. Crear entorno virtual
cd user-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
# Ajustar DATABASE_URL a localhost en lugar del nombre del contenedor

# 4. Ejecutar migraciones
alembic upgrade head

# 5. Iniciar servicio
uvicorn src.main:app --reload --port 8001
```

### Migraciones con Alembic

```bash
# Crear nueva migración
docker-compose exec user-service alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose exec user-service alembic upgrade head

# Revertir última migración
docker-compose exec user-service alembic downgrade -1

# Ver historial
docker-compose exec user-service alembic history
```

### Comandos útiles de Docker

```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ ELIMINA DATOS)
docker-compose down -v

# Reconstruir un servicio específico
docker-compose build user-service

# Reiniciar un servicio
docker-compose restart user-service

# Ver logs en tiempo real
docker-compose logs -f --tail=100 user-service

# Ejecutar comando en contenedor
docker-compose exec user-service bash

# Ver estado de servicios
docker-compose ps
```

## 🧪 Testing

```bash
# Ejecutar tests de un servicio
cd user-service
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
```

## 📚 Documentación

- **[Arquitectura de Microservicios](docs/ARQUITECTURA_MICROSERVICIOS.md)** - Diseño detallado
- **[Modelos SQLAlchemy](docs/MODELOS_SQLALCHEMY.md)** - Esquemas de BD
- **[Requerimientos](Requirements.md)** - Especificaciones funcionales
- **[Sprint 1](Sprint1.md)** - Planning del sprint actual
- **[Historias de Usuario](Historias.md)** - User stories completas

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT con expiración configurable (30 min por defecto)
- ✅ Validación de contraseñas seguras (8+ chars, mayúsculas, números)
- ✅ CORS configurado por servicio
- ✅ Variables sensibles en `.env` (git ignored)
- ⏳ HTTPS en producción (configurar reverse proxy)
- ⏳ Rate limiting en API Gateway
- ⏳ Refresh tokens

## 📝 TODO List

### Inmediato (Sprint 1)
- [x] F-02: Implementar gestión de roles y permisos
- [x] F-08: Implementar catálogo de servicios
- [x] F-09: Búsqueda y visualización de servicios
- [x] F-10: Gestión económica del catálogo
- [x] F-11: Creación y gestión de órdenes
- [x] F-12: Control económico de órdenes
- [x] F-13: Control administrativo de órdenes
- [x] F-27: Reportes operativos básicos
### Próximos Pasos (Sprint 2)
- [ ] F-04: Registro y mantenimiento de pacientes
- [ ] F-03: Gestión del perfil del usuario
- [ ] F-31: Parámetros fiscales y técnicos
- [ ] F-16: Gestión documental de comprobantes

### Mejoras técnicas
- [ ] Implementar refresh tokens
- [ ] Agregar tests unitarios y de integración
- [ ] Configurar CI/CD
- [ ] Agregar logging estructurado
- [ ] Implementar health checks avanzados
- [ ] Configurar Prometheus + Grafana para monitoreo
- [ ] Agregar rate limiting
- [ ] Implementar caché con Redis

### Futuro (Sprints 2-4)
- [ ] Gestión de pacientes completa
- [ ] Integración con laboratorio (LIS)
- [ ] Facturación electrónica SUNAT
- [ ] Notificaciones (Email, WhatsApp)
- [ ] Sistema de backup automático
- [ ] Dashboard analítico
- [ ] Exportación de reportes

## 👥 Equipo

- **William** - User Service (Auth, Roles)
- **Miguel** - Catalog Service, Configuration
- **Diego** - Catalog Economic Module
- **Eduard** - Order Service
- **Christian** - Order Economic/Admin Controls
- **Cristian** - Reporting Service

## 📄 Licencia

Este proyecto es privado y confidencial.

---

**Última actualización:** 20 de noviembre de 2025
**Versión:** 0.1.0 (Sprint 1 - En progreso)
**Última actualización:** 23 de noviembre de 2025
**Versión:** 1.0.0 (Sprint 1 - Completado)

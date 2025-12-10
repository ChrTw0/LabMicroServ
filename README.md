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

## 🚦 Estado del Proyecto

**Sprint Actual:** Sprint 4

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

- ✅ F-08: Gestión del catálogo
- ✅ F-09: Visualización y búsqueda de servicios
- ✅ F-10: Gestión económica del catálogo
- ✅ F-11: Creación y gestión de órdenes
- ✅ F-12: Control económico de órdenes
- ✅ F-13: Control administrativo de órdenes
- ✅ F-27: Reportes operativos
- 
### 📋 Sprint 2

- ✅ F-03:Gestión del perfil de usuario
- ✅ F-04:Registro y mantenimiento de pacientes
- ✅ F-31:Parámetros fiscales y técnicos
- ✅ F-16:Gestión documental de comprobantes

### 📋 Sprint 3

- ✅ F-06:Consulta e historial clínico
- ✅ F-23:Gestión de discrepancias
- ✅ F-22:Reportes financieros
- ✅ F-20:Monitoreo y reenvío de notificaciones
- ✅ F-21:Conciliación automática diaria
- ✅ F-24:Sincronización automática
- ✅ F-26:Visualización de KPIs
- ✅ F-19:Alertas operativas

### 📋 Sprint 4

- ⏸️ F-05:Búsqueda y validación de datos
- ⏸️ F-14:Emisión automática de comprobantes
- ⏸️ F-17:Notificaciones automáticas al paciente
- ⏸️ F-25:Gestión técnica de integración
- ⏸️ F-32:Parámetros locales
- ⏸️ F-07:Exportación y reportes de pacientes
- ⏸️ F-28:Análisis de tendencias
- ⏸️ F-29:Interacción y exportación
- ⏸️ F-18:Gestión de comunicación institucional
- ⏸️ F-33:Backup y restauración
- ⏸️ F-15:Cumplimiento tributario y validación

  
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

**Base de datos:** `order_db` (9 tablas)

### 4. Billing Service (Port 8004) ✅
**Estado:** Funcional - Integración SUNAT completada

**Funcionalidades:**
- ✅ Generación XML UBL 2.1 (estándar SUNAT)
- ✅ Firma digital de comprobantes
- ✅ Envío a SUNAT Beta/Producción vía SOAP
- ✅ Emisión de Facturas (01) y Boletas (03)
- ✅ Procesamiento de CDR (Constancia de Recepción)
- ✅ Manejo de estados tributarios
- ✅ CRUD completo de facturas
- ✅ Estadísticas y reportes de facturación
- ✅ Anulación de comprobantes
- ✅ Reenvío a SUNAT

**Módulos:**
- **Billing:** Facturación electrónica SUNAT ✅
- **SUNAT Integration:** Cliente SOAP + generador XML UBL 2.1 ✅
- **Reconciliation:** Conciliación y cierre de caja 🔧

**Endpoints disponibles:** 15+
- Creación de facturas/boletas
- Consulta y filtros
- Envío/reenvío a SUNAT
- Descarga de XML/CDR
- Anulación
- Estadísticas

**Base de datos:** `billing_db` (5 tablas)

**Integración SUNAT:**
- Ambiente Beta configurado (credenciales MODDATOS)
- Certificado autofirmado para pruebas
- Listo para producción (requiere certificado real)

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
| `billing_db` | 5435 | billing-service | 5 | ✅ Migrado |
| `config_db` | 5436 | configuration-service | 5 | ✅ Migrado |

### Credenciales por defecto (Development):

```
Usuario: postgres
Password: 1234
```

**⚠️ CAMBIAR EN PRODUCCIÓN**

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT con expiración configurable (30 min por defecto)
- ✅ Validación de contraseñas seguras (8+ chars, mayúsculas, números)
- ✅ CORS configurado por servicio
- ✅ Variables sensibles en `.env` (git ignored)
- ⏳ HTTPS en producción (configurar reverse proxy)
- ⏳ Rate limiting en API Gateway
- ⏳ Refresh tokens

## 👥 Equipo

- **William** - User Service (Auth, Roles)
- **Miguel** - Catalog Service, Configuration
- **Diego** - Catalog Economic Module
- **Eduard** - Order Service
- **Christian** - Order Economic/Admin Controls
- **Cristian** - Reporting Service
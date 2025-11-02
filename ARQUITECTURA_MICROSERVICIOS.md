# 🏗️ Arquitectura de Microservicios - Sistema de Gestión de Laboratorio Clínico

**Versión:** 2.0 (Refactorizada)
**Fecha:** 2025-10-31
**Escala:** Multi-sede (6 sedes)

## 📋 Resumen Ejecutivo

Sistema de gestión integral para laboratorios clínicos con **facturación electrónica SUNAT**, implementado como arquitectura de microservicios con FastAPI, optimizado para **6 sedes simultáneas** con **~600 órdenes diarias**.

### **Evolución de Arquitectura:**
- ❌ **v1.0:** 11 microservicios (sobre-ingeniería)
- ✅ **v2.0:** 7 microservicios (pragmático y escalable)

---

## 🎯 Microservicios Identificados (7 Servicios)

Arquitectura refactorizada con **fusión estratégica** de servicios con alta cohesión:

| # | Servicio | Puerto | Base de Datos | Responsabilidad | Escala |
|---|----------|--------|---------------|-----------------|--------|
| 1 | **user-service** | 8001 | `user_db` | 🔐 Autenticación, usuarios, roles | 2 pods |
| 2 | **patient-service** | 8002 | `patient_db` | 🧑‍🤝‍🧑 Gestión de pacientes, búsqueda, historial | 2 pods |
| 3 | **order-service** ⭐ | 8004 | `order_db` | 📦 Órdenes + Catálogo + Lab-sync | 4 pods |
| 4 | **billing-service** ⭐ | 8005 | `billing_db` | 💵 Facturación SUNAT + Conciliación | 3 pods |
| 5 | **core-service** ⭐ | 8010 | `config_db` | ⚙️ Configuración + Notificaciones | 2 pods |
| 6 | **reporting-service** | 8009 | Redis 💾 | 📊 Dashboard, reportes, KPIs | 3 pods |
| 7 | **api-gateway** | 8000 | - | 🚪 Routing, auth, rate limiting | 3 pods |

**Leyenda:**
- ⭐ = Servicio fusionado (contiene múltiples módulos)
- 💾 = Solo cache (Redis), sin PostgreSQL
- **pods** = Instancias recomendadas en producción

---

## 🔄 Justificación de Fusiones

### **1. order-service** (Fusiona 3 servicios)

**Servicios originales fusionados:**
- ❌ `catalog-service` → ✅ Módulo interno `src/modules/catalog/`
- ❌ `laboratory-integration-service` → ✅ Módulo event-driven `src/modules/lab_integration/`
- ✅ `order-service` (core)

**Razones:**
- 📋 El catálogo **solo existe para las órdenes** (no tiene sentido independiente)
- 🔬 La sincronización con laboratorio **se dispara al crear orden** (event-driven)
- 🗄️ Comparten la misma base de datos (`order_db`)
- ⚡ Reduce latencia (sin llamadas HTTP entre servicios)

**Estructura modular:**
```
order-service/
├── src/
│   ├── modules/
│   │   ├── catalog/           # Catálogo de servicios
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── orders/            # Órdenes de servicio
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── lab_integration/   # Sincronización laboratorio
│   │       ├── models.py      # LabSyncLog
│   │       ├── service.py
│   │       └── events.py      # Event consumer
│   ├── events/                # RabbitMQ producers
│   │   └── order_events.py
│   └── main.py
```

**Eventos emitidos:**
- `order.created` → Trigger automático de sincronización con laboratorio
- `order.completed` → Notificar a billing-service

---

### **2. billing-service** (Fusiona 2 servicios)

**Servicios originales fusionados:**
- ✅ `billing-service` (core)
- ❌ `reconciliation-service` → ✅ Módulo interno `src/modules/reconciliation/`

**Razones:**
- 💰 La conciliación es la **culminación del ciclo de facturación diario**
- 🗄️ Comparten la misma base de datos (`billing_db`)
- 📊 Reconciliación necesita leer facturas (queries JOIN eficientes)
- ⏰ Ambos trabajan con el mismo dominio temporal (cierre de día)

**Estructura modular:**
```
billing-service/
├── src/
│   ├── modules/
│   │   ├── billing/           # Facturación electrónica
│   │   │   ├── models.py      # Invoice, CreditNote, SunatResponse
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── sunat_client.py
│   │   └── reconciliation/    # Conciliación y cierre de caja
│   │       ├── models.py      # DailyClosure, CashCount, Discrepancy
│   │       ├── schemas.py
│   │       ├── service.py
│   │       └── router.py
│   ├── jobs/                  # Scheduled tasks
│   │   └── daily_reconciliation.py  # Cron job 11:59 PM
│   └── main.py
```

**Jobs programados:**
- ⏰ Conciliación automática diaria (11:59 PM por sede)
- 📧 Alertas de discrepancias a supervisores

---

### **3. core-service** (Fusiona 2 servicios)

**Servicios originales fusionados:**
- ✅ `configuration-service` (core)
- ❌ `notification-service` → ✅ Módulo interno `src/modules/notifications/`

**Razones:**
- 🛠️ Ambos son **servicios utilitarios** (no dominio de negocio)
- 🗄️ Comparten la misma base de datos (`config_db`)
- 📧 Las plantillas de notificación **son configuración del sistema**
- ⚙️ Configuración y comunicación están conceptualmente relacionadas

**Estructura modular:**
```
core-service/
├── src/
│   ├── modules/
│   │   ├── configuration/     # Configuración del sistema
│   │   │   ├── models.py      # CompanyInfo, Location, SystemSetting
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── notifications/     # Envío de notificaciones
│   │       ├── models.py      # NotificationLog, NotificationTemplate
│   │       ├── schemas.py
│   │       ├── service.py
│   │       ├── router.py
│   │       ├── email_sender.py
│   │       └── whatsapp_sender.py
│   ├── consumers/             # RabbitMQ consumers
│   │   └── notification_consumer.py
│   ├── jobs/                  # Scheduled tasks
│   │   └── daily_backup.py
│   └── main.py
```

**Eventos consumidos:**
- `order.created` → Enviar confirmación al paciente
- `invoice.issued` → Enviar comprobante por email/WhatsApp
- `reconciliation.discrepancy` → Alertar supervisores

---

## 🏛️ Arquitectura de Alto Nivel (7 Microservicios)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENTES (6 SEDES)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web Dashboard│  │ Mobile App   │  │  APIs Ext.   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (8000)                           │
│  - Autenticación JWT centralizada                               │
│  - Rate Limiting (por sede)                                     │
│  - Request Routing                                              │
│  - Load Balancing                                               │
│  - Circuit Breaker                                              │
│                                                                 │
│  3 pods (Alta Disponibilidad)                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ USER SERVICE │    │PATIENT SERVICE│   │  ORDER SERVICE   │
│    (8001)    │    │    (8002)     │   │     (8004)       │
│              │    │               │   │                  │
│  user_db     │    │  patient_db   │   │ + CATALOG        │
│              │    │               │   │ + LAB-SYNC       │
│  2 pods      │    │  2 pods       │   │                  │
└──────────────┘    └───────────────┘   │  order_db ⭐     │
                                        │                  │
                                        │  4 pods (CORE)   │
                                        └─────────┬────────┘
                                                  │
              ┌───────────────────────────────────┼──────────────┐
              │                                   │              │
              ▼                                   ▼              ▼
    ┌──────────────────┐              ┌──────────────┐  ┌──────────────┐
    │ BILLING SERVICE  │              │ CORE SERVICE │  │  REPORTING   │
    │     (8005)       │              │   (8010)     │  │   SERVICE    │
    │                  │              │              │  │   (8009)     │
    │ + RECONCILIATION │              │ + CONFIG     │  │              │
    │                  │              │ + NOTIFY     │  │  Redis ONLY  │
    │  billing_db ⭐   │              │              │  │              │
    │                  │              │  config_db ⭐│  │  3 pods      │
    │  3 pods          │              │              │  └──────────────┘
    └──────────────────┘              │  2 pods      │
                                      └──────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRAESTRUCTURA                              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  RabbitMQ   │  │    Redis    │  │   MinIO     │            │
│  │  (Events)   │  │   (Cache)   │  │ (Storage)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌──────────────────────────────────────────────┐              │
│  │  PostgreSQL - 5 BASES DE DATOS:              │              │
│  │  1. user_db         (Puerto 5432)            │              │
│  │  2. patient_db      (Puerto 5433)            │              │
│  │  3. order_db        (Puerto 5435) ⭐         │              │
│  │  4. billing_db      (Puerto 5436) ⭐         │              │
│  │  5. config_db       (Puerto 5437) ⭐         │              │
│  └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ SUNAT/PSE    │  │ SMTP Server  │  │ WhatsApp API │         │
│  │ (Facturación)│  │   (Email)    │  │  (Messages)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

**Nota:** ⭐ = Base de datos compartida entre módulos del mismo servicio

---

## 📦 Detalle de Microservicios Refactorizados

### 1. **user-service** (Sin cambios)

**Puerto:** 8001
**Base de Datos:** `user_db` (PostgreSQL, Puerto 5432)
**Instancias:** 2 pods

**Responsabilidad:**
- Autenticación y autorización (JWT)
- Gestión de usuarios (CRUD)
- Gestión de roles (Admin, Recepcionista, Supervisor, Laboratorista)
- Asignación de sedes a usuarios
- Recuperación de contraseña
- Perfil de usuario

**Modelos:**
- `User`, `Role`, `UserRole`, `PasswordResetToken`, `AuditLog`

**Endpoints Principales:**
```
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/forgot-password
POST   /auth/reset-password
GET    /users
POST   /users
GET    /users/{id}
PUT    /users/{id}
DELETE /users/{id}
GET    /roles
```

**Dependencias:**
- core-service (obtener info de sedes)

---

### 2. **patient-service** (Sin cambios)

**Puerto:** 8002
**Base de Datos:** `patient_db` (PostgreSQL, Puerto 5433)
**Instancias:** 2 pods

**Responsabilidad:**
- Registro de pacientes (DNI/RUC)
- Búsqueda de pacientes
- Actualización de datos
- Historial de órdenes por paciente
- Identificación de pacientes recurrentes
- Exportación a Excel

**Modelos:**
- `Patient`, `PatientHistory`, `PatientNote`

**Endpoints Principales:**
```
GET    /patients
POST   /patients
GET    /patients/{id}
PUT    /patients/{id}
GET    /patients/search?q=
GET    /patients/{id}/orders
GET    /patients/{id}/history
GET    /patients/recurring
GET    /patients/export
```

**Dependencias:**
- order-service (para historial de órdenes)

---

### 3. **order-service** ⭐ (FUSIONADO)

**Puerto:** 8004
**Base de Datos:** `order_db` (PostgreSQL, Puerto 5435)
**Instancias:** 4 pods (servicio core del negocio)

**Componentes fusionados:**
1. **Catálogo de Servicios** (antes catalog-service)
2. **Órdenes de Servicio** (core)
3. **Sincronización con Laboratorio** (antes laboratory-integration-service)

**Responsabilidad:**
- **Catálogo:** Gestión de servicios/exámenes, categorías, precios
- **Órdenes:** Creación, estados, descuentos, pagos
- **Lab-sync:** Sincronización automática con sistema de laboratorio

**Modelos:**
- **Catalog:** `Category`, `Service`, `PriceHistory`
- **Orders:** `Order`, `OrderItem`, `OrderPayment`, `OrderDiscount`, `OrderStatusHistory`
- **Lab-sync:** `LabSyncLog`

**Endpoints Principales:**
```
# Catálogo
GET    /catalog/services
POST   /catalog/services
GET    /catalog/services/{id}
PUT    /catalog/services/{id}
GET    /catalog/categories

# Órdenes
GET    /orders
POST   /orders
GET    /orders/{id}
PUT    /orders/{id}
GET    /orders/{id}/status
PUT    /orders/{id}/status
POST   /orders/{id}/discount
POST   /orders/{id}/cancel

# Lab Sync
POST   /lab-sync/sync/{order_id}
GET    /lab-sync/logs
GET    /lab-sync/pending
```

**Comunicación Asíncrona (RabbitMQ):**
- **Produce:**
  - `order.created` → Trigger sincronización con laboratorio (interno)
  - `order.created` → billing-service, core-service (externo)
  - `order.completed` → billing-service

**Dependencias:**
- patient-service (validar paciente)
- user-service (validar usuario)
- core-service (obtener configuración de sede)

---

#### Módulo de Catálogo (Fusionado)

**Responsabilidad:**
- Catálogo de servicios/exámenes
- Categorías de servicios
- Gestión de precios
- Historial de cambios de precios
- Activar/desactivar servicios

**Endpoints Detallados:**
```
GET    /catalog/services
POST   /catalog/services
GET    /catalog/services/{id}
PUT    /catalog/services/{id}
DELETE /catalog/services/{id}
GET    /catalog/services/active
GET    /catalog/services/search?q=
GET    /catalog/categories
POST   /catalog/categories
GET    /catalog/services/{id}/price-history
```

---

#### Módulo de Integración de Laboratorio (Fusionado)

**Responsabilidad:**
- Sincronización automática de órdenes con sistema de laboratorio
- Reintentos automáticos
- Log de sincronizaciones
- Sincronización manual forzada
- Soporte para API REST o exportación archivo

**Endpoints Detallados:**
```
POST   /lab-sync/sync
POST   /lab-sync/sync/{order_id}
GET    /lab-sync/logs
GET    /lab-sync/pending
POST   /lab-sync/retry/{log_id}
```

**Comunicación Asíncrona:**
- Consume evento `order.created` → sincronizar automáticamente

**Servicios Externos:**
- Sistema de Laboratorio (API REST o FTP)

---

### 4. **billing-service** ⭐ (FUSIONADO)

**Puerto:** 8005
**Base de Datos:** `billing_db` (PostgreSQL, Puerto 5436)
**Instancias:** 3 pods

**Componentes fusionados:**
1. **Facturación Electrónica** (core)
2. **Conciliación y Cierre de Caja** (antes reconciliation-service)

**Responsabilidad:**
- **Facturación:** Emisión boletas/facturas, integración SUNAT, CDR
- **Conciliación:** Cierre de caja diario, detección de discrepancias

**Modelos:**
- **Billing:** `Invoice`, `InvoiceItem`, `SunatResponse`, `CreditNote`, `InvoiceAudit`
- **Reconciliation:** `DailyClosure`, `CashCount`, `Discrepancy`

**Endpoints Principales:**
```
# Facturación
POST   /billing/invoice
POST   /billing/receipt
GET    /billing/{id}
GET    /billing/by-order/{order_id}
POST   /billing/{id}/credit-note
GET    /billing/{id}/pdf
GET    /billing/{id}/xml
POST   /billing/{id}/resend

# Conciliación
POST   /reconciliation/execute
GET    /reconciliation/closures
GET    /reconciliation/closures/{id}
POST   /reconciliation/closures/{id}/reopen
GET    /reconciliation/discrepancies
GET    /reconciliation/closures/{id}/export
```

**Jobs Programados:**
- ⏰ **Conciliación automática diaria** (11:59 PM por sede)

**Comunicación Asíncrona:**
- **Consume:**
  - `order.created` → Emitir comprobante
- **Produce:**
  - `invoice.issued` → core-service (enviar al paciente)
  - `reconciliation.discrepancy` → core-service (alertar supervisores)

**Dependencias:**
- order-service (obtener datos de orden)
- patient-service (datos fiscales del cliente)
- core-service (credenciales SUNAT, configuración)

**Servicios Externos:**
- SUNAT/PSE API

---

#### Módulo de Conciliación (Fusionado)

**Responsabilidad:**
- Conciliación automática diaria
- Comparación órdenes vs comprobantes vs pagos
- Detección de discrepancias
- Cierre de caja por sede
- Cálculo de efectivo esperado vs registrado
- Reabrir cierres de caja
- Exportación de reportes de cierre

**Jobs Programados:**
- Conciliación diaria automática (configurable, ej. 11:59 PM)

---

### 5. **core-service** ⭐ (FUSIONADO)

**Puerto:** 8010
**Base de Datos:** `config_db` (PostgreSQL, Puerto 5437)
**Instancias:** 2 pods

**Componentes fusionados:**
1. **Configuración del Sistema** (antes configuration-service)
2. **Notificaciones** (antes notification-service)

**Responsabilidad:**
- **Configuración:** Sedes, empresa, parámetros del sistema, backups
- **Notificaciones:** Emails, WhatsApp, alertas, plantillas

**Modelos:**
- **Configuration:** `CompanyInfo`, `Location`, `SystemSetting`, `BackupLog`
- **Notifications:** `NotificationLog`, `NotificationTemplate`, `NotificationRecipient`

**Endpoints Principales:**
```
# Configuración
GET    /config/company
PUT    /config/company
GET    /config/locations
POST   /config/locations
GET    /config/settings
PUT    /config/settings
POST   /config/backup
POST   /config/restore
GET    /config/backups

# Notificaciones
POST   /notifications/email
POST   /notifications/whatsapp
POST   /notifications/alert
GET    /notifications/history
POST   /notifications/{id}/resend
GET    /notifications/templates
POST   /notifications/templates
```

**Comunicación Asíncrona:**
- **Consume:**
  - `order.created` → Enviar confirmación
  - `invoice.issued` → Enviar comprobante
  - `reconciliation.discrepancy` → Alertar supervisores

**Servicios Externos:**
- SMTP Server
- WhatsApp Business API

**Storage:**
- MinIO (backups, logos)

---

#### Módulo de Notificaciones (Fusionado)

**Responsabilidad:**
- Envío de emails (SMTP)
- Envío de WhatsApp (API)
- Gestión de plantillas HTML
- Notificaciones de alertas (email + SMS)
- Historial de notificaciones
- Reenvío de notificaciones fallidas

**Endpoints Detallados:**
```
POST   /notifications/email
POST   /notifications/whatsapp
POST   /notifications/alert
GET    /notifications/history
POST   /notifications/{id}/resend
GET    /templates
POST   /templates
PUT    /templates/{id}
```

---

### 6. **reporting-service** (Sin cambios)

**Puerto:** 8009
**Base de Datos:** Redis ONLY (sin PostgreSQL)
**Instancias:** 3 pods (queries pesados)

**Responsabilidad:**
- Dashboard con KPIs en tiempo real
- Reportes de órdenes/ventas por sede
- Servicios más solicitados
- Ventas por método de pago
- Comparación mensual
- Exportación a PDF/Excel

**Cache (Redis):**
```
- report:dashboard:{sede}:{date}      (TTL: 5 min)
- report:sales:{sede}:{from}:{to}     (TTL: 15 min)
- report:top-services:{from}:{to}     (TTL: 30 min)
```

**Endpoints Principales:**
```
GET    /reports/dashboard
GET    /reports/orders?from=&to=&sede=
GET    /reports/sales?from=&to=&sede=
GET    /reports/top-services?from=&to=
GET    /reports/payment-methods?from=&to=
GET    /reports/patients-analysis?from=&to=
GET    /reports/monthly-comparison
POST   /reports/export
```

**Dependencias:**
- order-service (datos de órdenes)
- billing-service (datos de facturación)
- patient-service (datos de pacientes)

---

### 7. **api-gateway** (Sin cambios)

**Puerto:** 8000
**Instancias:** 3 pods (alta disponibilidad)

**Responsabilidad:**
- Punto de entrada único
- Autenticación JWT centralizada
- Rate limiting (por sede)
- Request routing
- Load balancing
- Circuit breaker
- CORS

**Routing:**
```
/api/auth/*           → user-service
/api/users/*          → user-service
/api/patients/*       → patient-service
/api/catalog/*        → order-service
/api/orders/*         → order-service
/api/lab-sync/*       → order-service
/api/billing/*        → billing-service
/api/reconciliation/* → billing-service
/api/config/*         → core-service
/api/notifications/*  → core-service
/api/reports/*        → reporting-service
```

**Dependencias:**
- user-service (validación de JWT)

---

## 📊 Estrategia de Base de Datos (Optimizada)

### **5 Bases de Datos PostgreSQL:**

| # | Base de Datos | Puerto | Owner Service | Tablas | Justificación |
|---|---------------|--------|---------------|--------|---------------|
| 1 | **user_db** | 5432 | user-service | 5 | Independiente (seguridad crítica) |
| 2 | **patient_db** | 5433 | patient-service | 3 | Independiente (dominio propio) |
| 3 | **order_db** | 5435 | order-service | 11 | Fusión catalog + orders + lab-sync |
| 4 | **billing_db** | 5436 | billing-service | 8 | Fusión billing + reconciliation |
| 5 | **config_db** | 5437 | core-service | 7 | Fusión configuration + notifications |

### **Distribución de Tablas:**

#### **1. user_db** (Independiente)
```
- users
- roles
- user_roles
- password_reset_tokens
- audit_logs
```

#### **2. patient_db** (Independiente)
```
- patients
- patient_history
- patient_notes
```

#### **3. order_db** (Fusionada)
```
Módulo Catalog:
  - categories
  - services
  - price_history

Módulo Orders:
  - orders
  - order_items
  - order_payments
  - order_discounts
  - order_status_history

Módulo Lab-sync:
  - lab_sync_logs
```

#### **4. billing_db** (Fusionada)
```
Módulo Billing:
  - invoices
  - invoice_items
  - sunat_responses
  - credit_notes
  - invoice_audit

Módulo Reconciliation:
  - daily_closures
  - cash_counts
  - discrepancies
```

#### **5. config_db** (Fusionada)
```
Módulo Configuration:
  - company_info
  - locations (sedes)
  - system_settings
  - backup_logs

Módulo Notifications:
  - notification_logs
  - notification_templates
  - notification_recipients
```

---

## 🔄 Patrones de Comunicación

### **Síncrona (HTTP REST):**
```
Cliente → API Gateway → Microservicio

Ejemplos:
- order-service → patient-service (validar paciente)
- order-service → core-service (obtener config de sede)
- billing-service → order-service (obtener datos de orden)
```

### **Asíncrona (Event-Driven con RabbitMQ):**

**Eventos principales:**

| Evento | Publisher | Consumers | Propósito |
|--------|-----------|-----------|-----------|
| `order.created` | order-service | billing-service, core-service | Emitir factura, enviar confirmación |
| `order.completed` | order-service | billing-service | Actualizar estados |
| `order.cancelled` | order-service | billing-service, core-service | Emitir nota de crédito |
| `invoice.issued` | billing-service | core-service | Enviar comprobante al paciente |
| `reconciliation.discrepancy` | billing-service | core-service | Alertar supervisores |

---

## 🗄️ Stack Tecnológico

### **Backend:**
- **Framework:** FastAPI 0.115+
- **Lenguaje:** Python 3.11+
- **ORM:** SQLAlchemy 2.0 (Async)
- **Validación:** Pydantic v2
- **Base de Datos:** PostgreSQL 14+
- **Message Broker:** RabbitMQ 3.12+
- **Cache:** Redis 7+
- **Storage:** MinIO (S3-compatible)

### **Infraestructura:**
- **Containerización:** Docker + Docker Compose
- **Orquestación:** Kubernetes (recomendado para 6 sedes)
- **Reverse Proxy:** Nginx
- **Monitoring:** Prometheus + Grafana
- **Logging:** Loguru + ELK Stack
- **Tracing:** Jaeger (distributed tracing)

### **Servicios Externos:**
- **SUNAT/PSE:** API REST para facturación electrónica
- **SMTP:** Email transaccional
- **WhatsApp Business API:** Mensajería

---

## 📏 Estimaciones de Escala (6 Sedes)

### **Volumen de Datos:**

| Métrica | Por Sede/Día | 6 Sedes/Día | Mes | Año |
|---------|--------------|-------------|-----|-----|
| **Órdenes** | 50-150 | 300-900 | 9,000-27,000 | 108,000-324,000 |
| **Pacientes** | 40-120 | 240-720 | 7,200-21,600 | 86,400-259,200 |
| **Facturas** | 50-150 | 300-900 | 9,000-27,000 | 108,000-324,000 |
| **Notificaciones** | 100-300 | 600-1,800 | 18,000-54,000 | 216,000-648,000 |

### **Rendimiento Esperado:**

| Métrica | Objetivo | Microservicios |
|---------|----------|----------------|
| **Tiempo respuesta** | < 500ms | 200-400ms |
| **Throughput** | 100 req/s | 200+ req/s |
| **Disponibilidad** | 99.5% | 99.7%+ |
| **Usuarios concurrentes** | 30 | 50+ |
| **Recuperación ante fallos** | < 5 min | < 2 min |

---

## 🔐 Seguridad

### **Autenticación:**
- JWT tokens con expiración (30 min)
- Refresh tokens (7 días)
- Password hashing con bcrypt (10+ rounds)

### **Autorización:**
- RBAC (Role-Based Access Control)
- 4 roles: Administrador General, Recepcionista, Supervisor de Sede, Laboratorista
- Permisos granulares por endpoint

### **Comunicación:**
- HTTPS/TLS 1.2+ en producción
- JWT en headers para comunicación inter-servicios
- API Keys para servicios externos

### **Protección:**
- Rate limiting (100 req/min por usuario)
- CORS configurado por sede
- SQL Injection prevention
- XSS prevention
- CSRF protection

### **Auditoría:**
- Logging de todas las operaciones críticas
- Registro de quién, qué, cuándo
- Retención de logs por 12 meses

---

## 💰 Estimación de Costos (Cloud - AWS)

| Recurso | Especificación | Costo/mes (USD) |
|---------|----------------|-----------------|
| **Kubernetes Cluster** | 3 nodos t3.medium | ~$150 |
| **RDS PostgreSQL** | db.t3.small Multi-AZ | ~$60 |
| **ElastiCache Redis** | cache.t3.micro | ~$15 |
| **Application Load Balancer** | ALB | ~$25 |
| **S3 Storage** | Backups + archivos | ~$10 |
| **CloudWatch** | Monitoring | ~$20 |
| **Route53 + ACM** | DNS + SSL | ~$5 |
| **RabbitMQ** | t3.small | ~$30 |
| **TOTAL** | | **~$315/mes** |

**Por sede:** ~$52.50/mes

---

## 📊 Comparativa de Arquitecturas

| Métrica | 11 Microservicios | 7 Microservicios | Mejora |
|---------|-------------------|------------------|--------|
| **Servicios** | 11 | 7 | ✅ -36% |
| **Bases de Datos** | 6 | 5 | ✅ -17% |
| **Llamadas HTTP promedio** | 4-5 | 2-3 | ✅ -40% |
| **Latencia estimada** | ~800ms | ~400ms | ✅ -50% |
| **Pods en producción** | ~22 | ~19 | ✅ -14% |
| **Complejidad operacional** | ⚠️ MUY ALTA | ✅ MEDIA | ✅ |
| **Tiempo de desarrollo** | ~6 meses | ~4 meses | ✅ -33% |

---

## ⚡ Características No Funcionales

### **Rendimiento:**
- Tiempo de respuesta < 500ms
- Búsqueda de pacientes < 1s
- Emisión de comprobantes < 5s
- Soporte para 60 usuarios concurrentes
- Procesamiento de 600 órdenes/día

### **Disponibilidad:**
- 99.7% uptime
- Recuperación ante fallos < 2 min
- Backup automático diario
- Multi-instance (sin single point of failure)

### **Escalabilidad:**
- Horizontal Pod Autoscaling (HPA)
- Soportar hasta 10 sedes sin cambios arquitectónicos
- Escala independiente por servicio
- Cache Redis para queries frecuentes

### **Mantenibilidad:**
- Código limpio (PEP8)
- Documentación completa
- Tests automatizados (70% cobertura)
- Logs estructurados
- Health checks en todos los servicios

---

## 🚀 Despliegue

### **Desarrollo (Local):**
```bash
docker-compose up -d
```

### **Producción (Kubernetes):**
```bash
# Deploy con Helm
helm install lab-system ./helm-charts

# Escalar servicio específico
kubectl scale deployment order-service --replicas=4

# Ver estado
kubectl get pods -n lab-system
```

---

## 📝 Cumplimiento Normativo

### **SUNAT:**
- Facturación electrónica según normativa vigente
- Numeración autorizada por sede
- Formato UBL 2.1
- Firma digital
- CDR validation

### **Protección de Datos:**
- Ley N° 29733 (Perú)
- Encriptación de datos sensibles
- Retención de datos por 5 años
- Anonimización para reportes

---

## 🎯 Próximos Pasos

1. ✅ **Definir arquitectura refactorizada** (COMPLETADO)
2. ⏳ **Crear estructura modular de servicios fusionados**
3. ⏳ **Implementar modelos en cada servicio**
4. ⏳ **Configurar docker-compose.yml completo**
5. ⏳ **Implementar event-driven con RabbitMQ**
6. ⏳ **Configurar Kubernetes para multi-sede**
7. ⏳ **Testing e integración**
8. ⏳ **Documentación de deployment**

---

**Fecha de última actualización:** 2025-10-31
**Versión:** 2.0 (Refactorizada para 6 sedes)
**Autor:** Sistema de diseño basado en análisis pragmático de microservicios

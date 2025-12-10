# Endpoints Disponibles - Sistema de Laboratorio Clínico

## Puertos de Servicios (según docker-compose.yml)

| Servicio | Puerto | URL Base |
|----------|--------|----------|
| **API Gateway** | 8000 | http://localhost:8000 |
| **user-service** | 8001 | http://localhost:8001 |
| **patient-service** | 8002 | http://localhost:8002 |
| **order-service** | 8003 | http://localhost:8003 |
| **billing-service** | 8004 | http://localhost:8004 |
| **configuration-service** | 8005 | http://localhost:8005 |

---

## 🔐 USER-SERVICE (Puerto 8001)

### Auth Router (`/api/v1/auth`)
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar nuevo usuario
- `GET /api/v1/auth/me` - Obtener información del usuario actual
- `POST /api/v1/auth/change-password` - Cambiar contraseña
- `POST /api/v1/auth/request-password-reset` - Solicitar restablecimiento de contraseña
- `POST /api/v1/auth/reset-password` - Restablecer contraseña con token
- `POST /api/v1/auth/verify-token` - Verificar validez del token

### User Router (`/api/v1/users`)
- `GET /api/v1/users` - Listar usuarios
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID
- `POST /api/v1/users` - Crear usuario
- `PUT /api/v1/users/{user_id}` - Actualizar usuario
- `DELETE /api/v1/users/{user_id}` - Eliminar usuario
- `PUT /api/v1/users/{user_id}/activate` - Activar usuario
- `PUT /api/v1/users/{user_id}/deactivate` - Desactivar usuario

### Role Router (`/api/v1/roles`)
- `GET /api/v1/roles` - Listar roles
- `GET /api/v1/roles/{role_id}` - Obtener rol por ID
- `POST /api/v1/roles` - Crear rol
- `PUT /api/v1/roles/{role_id}` - Actualizar rol
- `DELETE /api/v1/roles/{role_id}` - Eliminar rol

### Profile Router (`/api/v1/profile`)
- `GET /api/v1/profile` - Obtener perfil del usuario actual
- `PUT /api/v1/profile` - Actualizar perfil del usuario actual

**Swagger UI:** http://localhost:8001/docs

---

## 👤 PATIENT-SERVICE (Puerto 8002)

### Patient Router (`/api/v1/patients`)
- `GET /api/v1/patients` - Listar pacientes (con paginación y filtros)
- `GET /api/v1/patients/{patient_id}` - Obtener paciente por ID
- `POST /api/v1/patients` - Crear paciente
- `PUT /api/v1/patients/{patient_id}` - Actualizar paciente
- `DELETE /api/v1/patients/{patient_id}` - Soft delete paciente
- `GET /api/v1/patients/{patient_id}/history` - Obtener historial de cambios
- `GET /api/v1/patients/{patient_id}/notes` - Obtener notas del paciente
- `POST /api/v1/patients/{patient_id}/notes` - Agregar nota al paciente

**Swagger UI:** http://localhost:8002/docs

---

## 📦 ORDER-SERVICE (Puerto 8003)

### Catalog Router (`/api/v1`)
- `GET /api/v1/categories` - Listar categorías de servicios
- `GET /api/v1/categories/{category_id}` - Obtener categoría por ID
- `POST /api/v1/categories` - Crear categoría
- `PUT /api/v1/categories/{category_id}` - Actualizar categoría
- `DELETE /api/v1/categories/{category_id}` - Eliminar categoría

- `GET /api/v1/services` - Listar servicios/exámenes
- `GET /api/v1/services/{service_id}` - Obtener servicio por ID
- `POST /api/v1/services` - Crear servicio
- `PUT /api/v1/services/{service_id}` - Actualizar servicio
- `DELETE /api/v1/services/{service_id}` - Eliminar servicio
- `PUT /api/v1/services/{service_id}/price` - Actualizar precio del servicio
- `GET /api/v1/services/{service_id}/price-history` - Obtener historial de precios

### Orders Router (`/api/v1/orders`)
- `GET /api/v1/orders` - Listar órdenes (con paginación y filtros)
- `GET /api/v1/orders/{order_id}` - Obtener orden por ID
- `POST /api/v1/orders` - Crear orden
- `PUT /api/v1/orders/{order_id}` - Actualizar orden
- `DELETE /api/v1/orders/{order_id}` - Eliminar orden
- `PUT /api/v1/orders/{order_id}/status` - Cambiar estado de orden
- `POST /api/v1/orders/{order_id}/payments` - Agregar pago a orden
- `GET /api/v1/orders/{order_id}/payments` - Obtener pagos de una orden

### Lab Integration Router (`/api/v1/lab-sync`)
- `GET /api/v1/lab-sync` - Listar logs de sincronización LIS
- `GET /api/v1/lab-sync/statistics` - Obtener estadísticas de sincronización
- `GET /api/v1/lab-sync/order/{order_id}` - Obtener log de sincronización por orden
- `GET /api/v1/lab-sync/{log_id}` - Obtener log de sincronización por ID
- `POST /api/v1/lab-sync` - Sincronizar orden con LIS
- `POST /api/v1/lab-sync/{log_id}/retry` - Reintentar sincronización fallida

**Swagger UI:** http://localhost:8003/docs

---

## 💰 BILLING-SERVICE (Puerto 8004)

### Billing Router (`/api/v1/invoices`)
- `GET /api/v1/invoices` - Listar comprobantes (con paginación y filtros)
- `GET /api/v1/invoices/{invoice_id}` - Obtener comprobante por ID
- `POST /api/v1/invoices` - Generar comprobante (Boleta o Factura)
- `PUT /api/v1/invoices/{invoice_id}` - Actualizar comprobante
- `DELETE /api/v1/invoices/{invoice_id}` - Anular comprobante
- `PUT /api/v1/invoices/{invoice_id}/status` - Actualizar estado del comprobante
- `GET /api/v1/invoices/statistics` - Obtener estadísticas de facturación

### SUNAT Integration (Sprint 2 - Mock)
- `GET /api/v1/invoices/{invoice_id}/ubl` - Obtener XML UBL del comprobante
- `GET /api/v1/invoices/{invoice_id}/cdr` - Obtener CDR de SUNAT
- `GET /api/v1/invoices/{invoice_id}/tributary-status` - Verificar estado tributario
- `POST /api/v1/invoices/{invoice_id}/resend` - Reenviar comprobante por email

**Swagger UI:** http://localhost:8004/docs

---

## ⚙️ CONFIGURATION-SERVICE (Puerto 8005)

### Configuration Router (`/api/v1`)

#### Locations (Sedes)
- `GET /api/v1/locations` - Listar sedes
- `GET /api/v1/locations/{location_id}` - Obtener sede por ID
- `POST /api/v1/locations` - Crear sede
- `PUT /api/v1/locations/{location_id}` - Actualizar sede
- `DELETE /api/v1/locations/{location_id}` - Eliminar sede

#### Company (Datos de la Empresa)
- `GET /api/v1/company` - Obtener datos de la empresa
- `POST /api/v1/company` - Crear datos de la empresa
- `PUT /api/v1/company/{company_id}` - Actualizar datos de la empresa

#### Settings (Configuraciones del Sistema)
- `GET /api/v1/settings` - Listar todas las configuraciones
- `GET /api/v1/settings/{key}` - Obtener configuración por clave
- `POST /api/v1/settings` - Crear configuración
- `PUT /api/v1/settings/{key}` - Actualizar configuración
- `DELETE /api/v1/settings/{key}` - Eliminar configuración
- `PUT /api/v1/settings/{key}/upsert` - Crear o actualizar configuración
- `POST /api/v1/settings/bulk` - Crear/actualizar múltiples configuraciones

**Swagger UI:** http://localhost:8005/docs

---

## 🌐 API-GATEWAY (Puerto 8000)

**Estado:** Configurado en docker-compose pero la implementación está pendiente.

El API Gateway debe:
- Routing unificado a todos los servicios
- Autenticación JWT centralizada
- Rate limiting
- Circuit breaker
- CORS centralizado

**Variables de entorno configuradas:**
```
USER_SERVICE_URL=http://user-service:8001
PATIENT_SERVICE_URL=http://patient-service:8002
ORDER_SERVICE_URL=http://order-service:8003
BILLING_SERVICE_URL=http://billing-service:8004
CONFIGURATION_SERVICE_URL=http://configuration-service:8005
```

---

## 📝 Notas para el Frontend

### Estado actual del Frontend
- **Ubicación:** `frontend/` (recuperado recientemente)
- **Stack:** Vite + React 19 + Axios
- **Estado:** Template básico, sin conexión a APIs aún

### Para conectar el frontend a los servicios:

#### Opción 1: Llamar directamente a cada servicio
```javascript
// Ejemplo con axios
const API_URLS = {
  auth: 'http://localhost:8001/api/v1/auth',
  users: 'http://localhost:8001/api/v1/users',
  patients: 'http://localhost:8002/api/v1/patients',
  orders: 'http://localhost:8003/api/v1/orders',
  catalog: 'http://localhost:8003/api/v1',
  billing: 'http://localhost:8004/api/v1/invoices',
  config: 'http://localhost:8005/api/v1'
};
```

#### Opción 2: A través del API Gateway (cuando esté implementado)
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Endpoints prioritarios para implementar en Frontend

1. **Autenticación:**
   - `POST /api/v1/auth/login`
   - `GET /api/v1/auth/me`

2. **Pacientes:**
   - `GET /api/v1/patients` (listado)
   - `POST /api/v1/patients` (crear)
   - `PUT /api/v1/patients/{id}` (editar)

3. **Catálogo:**
   - `GET /api/v1/services` (servicios/exámenes)
   - `GET /api/v1/categories` (categorías)

4. **Órdenes:**
   - `POST /api/v1/orders` (crear orden)
   - `GET /api/v1/orders` (listado)
   - `POST /api/v1/orders/{id}/payments` (registrar pago)

5. **Facturación:**
   - `POST /api/v1/invoices` (generar comprobante)
   - `GET /api/v1/invoices` (listado)

---

## 🔧 Testing de Endpoints

Todos los servicios tienen Swagger UI disponible:

```bash
# User Service
http://localhost:8001/docs

# Patient Service
http://localhost:8002/docs

# Order Service
http://localhost:8003/docs

# Billing Service
http://localhost:8004/docs

# Configuration Service
http://localhost:8005/docs
```

---

**Última actualización:** 2025-12-07
**Generado automáticamente desde los routers de cada microservicio**

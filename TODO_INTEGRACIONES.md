# TODOs y Pendientes - Integraciones

Este documento lista todas las integraciones y tareas pendientes identificadas durante el Sprint 1.

---

## 🔴 ALTA PRIORIDAD

### F-13: Integración con LIS (Laboratory Information System)

**Archivo:** `order-service/src/modules/lab_integration/service.py`

**Estado:** Endpoints creados, simulación activa, integración real pendiente

**Tareas:**

1. **Obtener documentación del LIS a integrar**
   - [ ] Solicitar manual de API del LIS
   - [ ] Identificar endpoints disponibles
   - [ ] Revisar esquema de datos requeridos
   - [ ] Verificar métodos de autenticación soportados

2. **Configurar credenciales de acceso**
   - [ ] Obtener API key o credenciales del LIS
   - [ ] Agregar a variables de entorno (.env):
     ```
     LIS_API_URL=https://api.lis-real.com/v1
     LIS_API_KEY=your-api-key-here
     LIS_API_SECRET=your-secret-here  # si aplica
     ```
   - [ ] Actualizar `src/core/config.py` con nuevas variables

3. **Implementar integración real**
   - [ ] Reemplazar `LIS_API_URL` en línea 44 con URL real
   - [ ] Descomentar y ajustar código de integración (líneas 108-169)
   - [ ] Eliminar código de simulación (líneas 172-176)
   - [ ] Ajustar payload según especificaciones del LIS
   - [ ] Implementar manejo de errores específicos del LIS

4. **Testing**
   - [ ] Probar sincronización exitosa
   - [ ] Probar manejo de errores (timeout, 4xx, 5xx)
   - [ ] Validar retry logic
   - [ ] Verificar logs en ambos sistemas

5. **Monitoreo**
   - [ ] Configurar alertas para sincronizaciones fallidas
   - [ ] Dashboard de estadísticas de sincronización
   - [ ] Logs centralizados

**Código de referencia:**
```python
# Ver: order-service/src/modules/lab_integration/service.py
# Líneas 102-170: Código de ejemplo para integración
```

**Referencias de documentación:**
- Swagger: http://localhost:8003/docs (sección Lab Integration)
- Endpoints disponibles: `/api/v1/lab-sync`

---

## 🟡 MEDIA PRIORIDAD

### Comunicación entre Servicios - Mejoras

**Estado:** Funcional con httpx directo, puede mejorarse

**Tareas:**

1. **Implementar Circuit Breaker Pattern**
   - [ ] Instalar `tenacity` o `resilience4j`
   - [ ] Agregar retry logic con backoff exponencial
   - [ ] Configurar circuit breaker para servicios críticos
   - [ ] Agregar fallbacks para servicios no disponibles

2. **Agregar Caché de Respuestas**
   - [ ] Implementar Redis para caché
   - [ ] Cachear respuestas de patient-service
   - [ ] Cachear catálogo de servicios
   - [ ] Configurar TTL apropiado

3. **Service Discovery**
   - [ ] Considerar Consul o Eureka para descubrimiento de servicios
   - [ ] Reemplazar URLs hardcodeadas
   - [ ] Load balancing automático

**Archivos afectados:**
- `billing-service/src/modules/billing/service.py` (líneas 16-17)
- Cualquier servicio que llame a otros servicios

---

### Autenticación en Endpoints

**Estado:** Endpoints públicos, autenticación pendiente

**Tareas:**

1. **Implementar middleware de autenticación**
   - [ ] Crear dependency `get_current_user` en cada servicio
   - [ ] Validar JWT token en headers
   - [ ] Verificar permisos según rol

2. **Proteger endpoints**
   - [ ] Agregar `dependencies=[Depends(get_current_user)]` a routers
   - [ ] Implementar RBAC (Role-Based Access Control)
   - [ ] Documentar permisos requeridos por endpoint

3. **Excepciones comunes**
   - Endpoints públicos: `/health`, `/`, `/docs`
   - Endpoints protegidos: Todos los CRUD

**Ejemplo de implementación:**
```python
# En cada router.py
from src.core.security import get_current_user

@router.get("/api/v1/resource")
async def get_resource(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar permisos aquí
    pass
```

---

### Facturación Electrónica - Integración SUNAT

**Estado:** Números correlativos generados, envío a SUNAT pendiente

**Archivo:** `billing-service/src/modules/billing/service.py`

**Tareas:**

1. **Investigar opciones de integración**
   - [ ] PSE (Proveedor de Servicios Electrónicos)
   - [ ] SOL (SUNAT Operaciones en Línea) directo
   - [ ] Facturador gratuito SUNAT

2. **Implementar firma digital**
   - [ ] Obtener certificado digital
   - [ ] Instalar librería de firma XML
   - [ ] Generar XML según estándar UBL 2.1

3. **Envío a SUNAT**
   - [ ] Implementar endpoint de envío
   - [ ] Manejar respuesta CDR (Constancia de Recepción)
   - [ ] Actualizar estado según respuesta SUNAT

4. **Casos especiales**
   - [ ] Notas de crédito
   - [ ] Notas de débito
   - [ ] Comunicaciones de baja

**Referencias:**
- Documentación SUNAT: https://cpe.sunat.gob.pe/

---

## 🟢 BAJA PRIORIDAD / MEJORAS

### Validaciones Adicionales

**Tareas:**

1. **Patient Service**
   - [ ] Validar formato de email con DNS check
   - [ ] Validar números de teléfono según operador
   - [ ] Detectar pacientes duplicados (fuzzy matching)

2. **Order Service**
   - [ ] Validar que servicios pertenezcan a categorías activas
   - [ ] Alertar si precio cambió desde creación de orden
   - [ ] Validar horarios de atención por sede

3. **Billing Service**
   - [ ] Validar RUC con API SUNAT
   - [ ] Límites de facturación diaria
   - [ ] Alertas de comprobantes rechazados

---

### Logging y Monitoring

**Tareas:**

1. **Centralizar logs**
   - [ ] Implementar ELK Stack (Elasticsearch, Loguru, Kibana)
   - [ ] O usar Grafana Loki
   - [ ] Configurar niveles de log por ambiente

2. **Métricas**
   - [ ] Prometheus para métricas
   - [ ] Grafana para visualización
   - [ ] Alertas por Slack/Email

3. **Tracing distribuido**
   - [ ] Implementar OpenTelemetry
   - [ ] Jaeger para visualización de traces
   - [ ] Correlación de requests entre servicios

---

### Testing

**Tareas:**

1. **Unit Tests**
   - [ ] pytest para cada servicio
   - [ ] Coverage mínimo 80%
   - [ ] Mocks de dependencias externas

2. **Integration Tests**
   - [ ] Testear comunicación entre servicios
   - [ ] Testear flujos completos (crear orden → facturar)
   - [ ] Testear con BD de pruebas

3. **E2E Tests**
   - [ ] Playwright o Selenium
   - [ ] Escenarios de usuario completos
   - [ ] Tests de regresión

4. **Performance Tests**
   - [ ] Locust o JMeter
   - [ ] Identificar cuellos de botella
   - [ ] Tests de carga

---

### Documentación

**Tareas:**

1. **README por servicio**
   - [ ] Descripción del servicio
   - [ ] Variables de entorno
   - [ ] Comandos de desarrollo
   - [ ] Arquitectura interna

2. **Guías de desarrollo**
   - [ ] Convenciones de código
   - [ ] Cómo agregar un nuevo endpoint
   - [ ] Cómo crear una migración
   - [ ] Troubleshooting común

3. **Diagramas**
   - [ ] Diagrama de arquitectura actualizado
   - [ ] Diagramas de secuencia por flujo
   - [ ] Modelo de datos por servicio

---

### DevOps y CI/CD

**Tareas:**

1. **CI/CD Pipeline**
   - [ ] GitHub Actions o GitLab CI
   - [ ] Build automático
   - [ ] Tests automáticos
   - [ ] Deploy a staging/production

2. **Ambientes**
   - [ ] Development (local)
   - [ ] Staging (pre-producción)
   - [ ] Production
   - [ ] Variables de entorno por ambiente

3. **Secrets Management**
   - [ ] Vault o AWS Secrets Manager
   - [ ] Rotación de credenciales
   - [ ] Encriptación de secrets

4. **Monitoreo de infraestructura**
   - [ ] Health checks automatizados
   - [ ] Auto-scaling
   - [ ] Disaster recovery plan

---

### Seguridad

**Tareas:**

1. **Seguridad de API**
   - [ ] Rate limiting por IP/usuario
   - [ ] CORS configurado apropiadamente
   - [ ] Validación de input (XSS, SQL injection)
   - [ ] Helmet.js equivalente para FastAPI

2. **Seguridad de datos**
   - [ ] Encriptación de datos sensibles en BD
   - [ ] Enmascaramiento de PII en logs
   - [ ] GDPR compliance (si aplica)

3. **Auditoría de seguridad**
   - [ ] Scan de vulnerabilidades (Snyk, SonarQube)
   - [ ] Pentesting
   - [ ] Revisión de dependencias

---

### Base de Datos

**Tareas:**

1. **Optimizaciones**
   - [ ] Índices en campos frecuentemente consultados
   - [ ] Particionamiento de tablas grandes
   - [ ] Archivado de datos antiguos

2. **Backups**
   - [ ] Backups automáticos diarios
   - [ ] Retención de 30 días
   - [ ] Testing de restauración

3. **Monitoring**
   - [ ] Slow query log
   - [ ] Conexiones activas
   - [ ] Tamaño de tablas

---

## 📋 Checklist de Producción

Antes de ir a producción, verificar:

### Infraestructura
- [ ] Variables de entorno configuradas
- [ ] Secrets seguros (no en código)
- [ ] HTTPS configurado
- [ ] Firewall configurado
- [ ] Backups automáticos activos

### Código
- [ ] Tests pasando (unit, integration)
- [ ] Code review completado
- [ ] Sin TODOs críticos en código
- [ ] Logging apropiado
- [ ] Manejo de errores robusto

### Documentación
- [ ] README actualizado
- [ ] API documentada (Swagger)
- [ ] Runbook de operaciones
- [ ] Plan de rollback

### Monitoring
- [ ] Health checks configurados
- [ ] Alertas configuradas
- [ ] Dashboard de métricas
- [ ] Logs centralizados

### Seguridad
- [ ] Autenticación en todos los endpoints
- [ ] Rate limiting activo
- [ ] Scan de vulnerabilidades pasado
- [ ] Secrets rotados

---

**Última actualización:** 2025-11-23

**Nota:** Este documento debe actualizarse conforme se completen tareas o se identifiquen nuevas.

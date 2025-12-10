# Manual de Usuario - Sistema de Laboratorio Clínico

Este documento proporciona una guía detallada sobre cómo utilizar las funcionalidades del Sistema de Gestión de Laboratorio Clínico.

## 1. Introducción

Bienvenido al sistema de gestión para laboratorios clínicos. Esta plataforma centraliza la gestión de pacientes, órdenes, facturación, y más, en una arquitectura de microservicios robusta y escalable.

## 2. Acceso al Sistema

Para ingresar al sistema, siga estos pasos:

1.  Abra su navegador web y diríjase a la URL de la aplicación (por defecto: `http://localhost:5173`).
2.  Ingrese su **email** y **contraseña** en el formulario de inicio de sesión.
3.  Haga clic en el botón "Iniciar Sesión".

Si las credenciales son correctas, será redirigido al **Dashboard** principal.

## 3. Descripción de Roles

El sistema cuenta con diferentes roles de usuario, cada uno con permisos específicos para acceder a distintas funcionalidades.

-   **Administrador General:** Tiene acceso a todas las funcionalidades del sistema, incluyendo la gestión de usuarios, roles, y configuración general.
-   **Recepcionista:** Encargado de la atención al cliente. Gestiona pacientes, crea órdenes de servicio y registra pagos.
-   **Supervisor de Sede:** Monitorea las operaciones de una sede específica. Tiene acceso a reportes y, en algunos casos, a la conciliación.
-   **Contador:** Responsable de la facturación, conciliación y reportes financieros.
-   **Laboratorista:** Encargado de procesar las órdenes y registrar los resultados de los análisis. Tiene acceso a las órdenes y al catálogo.
-   **Paciente:** Puede ver su historial de órdenes, resultados y facturas.

## 4. Guía por Módulos

A continuación, se describen las principales funcionalidades agrupadas por módulo.

### 4.1. Dashboard

El Dashboard es la pantalla principal después de iniciar sesión. Muestra un resumen general de la actividad del laboratorio, como:
-   Número de órdenes del día.
-   Ventas totales.
-   Estado de la conciliación.
-   Accesos directos a las funciones más utilizadas.

### 4.2. Gestión de Pacientes (Rol: Recepcionista, Administrador)

Este módulo permite gestionar la base de datos de pacientes.

**Para crear un nuevo paciente:**
1.  En el menú lateral, vaya a **Pacientes**.
2.  Haga clic en el botón **"Nuevo Paciente"**.
3.  Complete el formulario con la información del paciente. El formulario se ajusta según el tipo de documento (DNI/RUC).
4.  Haga clic en **"Guardar"**.

**Para buscar un paciente:**
1.  En la página de **Pacientes**, utilice la barra de búsqueda para buscar por nombre, DNI o RUC.
2.  Los resultados se mostrarán en la tabla.

**Para editar un paciente:**
1.  Busque al paciente que desea modificar.
2.  En la fila del paciente, haga clic en el botón de **"Editar"** (icono de lápiz).
3.  Modifique los datos en el formulario y haga clic en **"Guardar"**.

### 4.3. Catálogo de Servicios

El catálogo muestra todos los análisis y servicios que ofrece el laboratorio.

-   **Usuarios de solo lectura (Paciente, Recepcionista, etc.):** Pueden ver los servicios en una vista de cuadrícula o tabla, incluyendo nombre, código y precio.
-   **Usuarios con permisos de escritura (Administrador General):**
    -   Pueden ver la vista de tabla con opciones para **Crear, Editar y Eliminar** servicios.
    -   Pueden gestionar las **Categorías** de los servicios.
    -   Pueden ver el **Historial de Precios** de un servicio.

### 4.4. Gestión de Órdenes (Rol: Recepcionista)

Este es uno de los flujos de trabajo más importantes del sistema.

**Para crear una nueva orden:**
1.  En el menú lateral, vaya a **Órdenes**.
2.  Haga clic en **"Nueva Orden"**.
3.  **Seleccionar Paciente:**
    -   Utilice el campo de búsqueda para encontrar al paciente por nombre o documento.
    -   Seleccione al paciente de la lista desplegable.
4.  **Seleccionar Servicios:**
    -   Busque los servicios deseados por nombre o código.
    -   Haga clic en el botón **"+ Agregar"** para añadirlos a la orden.
    -   Puede ajustar la cantidad de cada servicio en la tabla de "Servicios Agregados".
5.  **Registrar Pagos (Opcional):**
    -   En la sección de pagos, seleccione el método de pago e ingrese el monto.
    -   Puede agregar múltiples pagos para una misma orden (pago mixto).
    -   El sistema calculará el total y el saldo pendiente automáticamente.
6.  **Crear Orden:**
    -   Haga clic en el botón **"Crear Orden"** para finalizar.

### 4.5. Facturación (Rol: Contador, Administrador)

Este módulo permite gestionar los comprobantes de pago electrónicos.

-   Desde la página de **Facturación**, puede ver una lista de todas las facturas y boletas emitidas.
-   Puede filtrar los comprobantes por fecha, cliente o estado.
-   Al hacer clic en un comprobante, puede ver su detalle completo.
-   La generación de comprobantes es automática al crear una orden que tiene asociado un pago.

### 4.6. Gestión de Usuarios (Rol: Administrador General)

Solo los administradores generales tienen acceso a esta sección.

-   **Usuarios:** Permite crear, ver, editar y desactivar las cuentas de usuario del sistema.
-   **Roles:** Permite gestionar los roles y los permisos asociados a cada uno.

### 4.7. Reportes (Rol: Contador, Laboratorista, Supervisor)

El módulo de reportes ofrece una visión analítica de las operaciones.
-   **Reporte de Ventas:** Desglosa las ventas por período, sede, etc.
-   **Top Servicios:** Muestra los servicios más solicitados.
-   **Pacientes Nuevos vs. Recurrentes:** Analiza la fidelización de pacientes.

Para generar un reporte:
1.  Vaya a la sección **Reportes**.
2.  Seleccione el tipo de reporte que desea ver.
3.  Utilice los filtros (fechas, sedes) para acotar la información.
4.  El sistema mostrará los datos en tablas y gráficos.

### 4.8. Conciliación (Rol: Contador)

Este módulo permite cuadrar las operaciones financieras del día.
-   Compara las órdenes creadas, los comprobantes emitidos y los pagos registrados.
-   Identifica y resalta discrepancias automáticamente.
-   Genera un reporte de cierre de caja por sede y método de pago.

## 5. Flujo de Trabajo Común: Atención Completa a un Paciente

1.  **Registro del Paciente:** Un recepcionista registra al paciente en el sistema a través del módulo de **Pacientes**. Si el paciente ya existe, se busca y selecciona.
2.  **Creación de la Orden:** El recepcionista va al módulo de **Órdenes**, crea una nueva orden, asocia al paciente y agrega los servicios que solicita.
3.  **Registro del Pago:** En la misma pantalla de la orden, el recepcionista registra el pago (total o parcial) realizado por el paciente.
4.  **Generación de Comprobante:** Al crear la orden con un pago, el sistema genera automáticamente el comprobante de pago electrónico (boleta o factura).
5.  **Procesamiento de Muestra:** El laboratorista ve la orden en estado "En Proceso" y realiza los análisis correspondientes.
6.  **Completar Orden:** Una vez finalizados los análisis, el laboratorista cambia el estado de la orden a "Completada".
7.  **Consulta de Resultados:** El paciente puede ingresar al sistema con su usuario y contraseña para ver el historial y los resultados de sus órdenes.

## 6. Preguntas Frecuentes (FAQ)

**P: ¿Qué hago si olvidé mi contraseña?**
**R:** En la página de inicio de sesión, haga clic en el enlace "¿Olvidó su contraseña?" y siga las instrucciones para restablecerla a través de su correo electrónico.

**P: ¿Por qué no puedo ver el módulo de "Usuarios"?**
**R:** El acceso a ciertos módulos está restringido por roles. La gestión de usuarios solo está disponible para el "Administrador General".

**P: ¿Puedo editar una orden después de crearla?**
**R:** Sí, puede editar una orden mientras se encuentre en estado "Registrada" o "En Proceso". No se pueden modificar órdenes "Completadas" o "Anuladas".

**P: ¿Cómo se genera una factura en lugar de una boleta?**
**R:** El sistema genera una factura automáticamente si el paciente tiene registrado un **RUC**. Si solo tiene DNI u otro documento, se generará una boleta.

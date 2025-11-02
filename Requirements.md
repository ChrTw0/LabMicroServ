```markdown
## Módulo de Gestión de Usuarios y Autenticación

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-001** | Paciente | Iniciar sesión mediante usuario y contraseña. | Acceder de forma segura al sistema. | - El sistema valida usuario y contraseña.<br>- Solo usuarios activos pueden acceder.<br>- Se muestra mensaje de error si las credenciales son incorrectas.<br>- Tras iniciar sesión, se redirige al panel según su rol. |
| **RF-002** | Administrador General | Gestionar los roles de los usuarios (Administrador, Recepcionista, Supervisor, Laboratorista). | Controlar los permisos y accesos dentro del sistema. | - El sistema permite asignar y cambiar roles de usuarios existentes.<br>- Solo el Administrador General puede modificar roles.<br>- Cada rol tiene acceso restringido a sus funciones.<br>- Los cambios de rol se registran con fecha y usuario responsable. |
| **RF-003** | Paciente | Cerrar sesión de forma segura. | Finalizar la sesión actual y proteger la cuenta del usuario. | - El sistema cierra la sesión actual al solicitarlo.<br>- Se elimina la sesión activa del navegador.<br>- Se redirige al formulario de inicio de sesión. |
| **RF-004** | Paciente | Recuperar su contraseña mediante correo electrónico. | Restablecer el acceso en caso de olvido o pérdida de contraseña. | - El usuario puede solicitar recuperación ingresando su email registrado.<br>- El sistema envía un enlace temporal para restablecer la contraseña.<br>- El enlace expira después de un tiempo determinado.<br>- La nueva contraseña debe cumplir con las políticas de seguridad. |
| **RF-005** | Administrador General | Crear, modificar y desactivar usuarios del sistema. | Mantener actualizada la base de usuarios. | - El sistema permite registrar nuevos usuarios con nombre, email, rol y sede.<br>- Se pueden editar los datos existentes.<br>- Los usuarios pueden desactivarse sin ser eliminados.<br>- Se registra la fecha y el usuario que realiza cada acción. |
| **RF-006** | Administrador General | Asignar una sede específica a cada usuario. | Organizar correctamente el personal según su ubicación. | - Durante la creación o edición de usuarios, se debe asignar una sede.<br>- Un usuario solo puede pertenecer a una sede a la vez.<br>- Los usuarios pueden filtrarse por sede.<br>- Solo el Administrador General puede realizar esta asignación. |
| **RF-007** | Paciente | Ver y actualizar su información de perfil. | Mantener actualizados sus datos personales. | - El usuario puede acceder a su perfil desde el menú principal.<br>- Puede actualizar información básica (nombre, email, contraseña).<br>- Los cambios se guardan inmediatamente y se confirman al usuario.<br>- El sistema valida los datos antes de actualizar. |

## Módulo de Gestión de Pacientes

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-008** | Administrador General, Recepcionista | Registrar nuevos pacientes con DNI/RUC, nombres, teléfono, email y dirección. | Mantener actualizada la base de datos de pacientes. | - El sistema permite registrar un nuevo paciente ingresando los campos requeridos.<br>- Se valida que el DNI o RUC no estén duplicados.<br>- Al guardar, se muestra confirmación del registro exitoso.<br>- Solo usuarios autorizados pueden realizar el registro. |
| **RF-009** | Supervisor de Sede, Recepcionista | Buscar pacientes por DNI, RUC, nombres o apellidos. | Localizar rápidamente la información de un paciente. | - Se dispone de un campo de búsqueda con coincidencias parciales.<br>- Los resultados se muestran en tiempo real o tras presionar “Buscar”.<br>- Se puede ordenar y filtrar por tipo de documento o nombre. |
| **RF-010** | Administrador General, Recepcionista | Actualizar la información de pacientes existentes. | Corregir o completar datos registrados. | - El sistema permite editar datos personales, contacto y dirección.<br>- Se registra la fecha y usuario que realizó la modificación.<br>- No se permiten duplicados de DNI/RUC.<br>- Se muestra un mensaje de confirmación tras guardar los cambios. |
| **RF-011** | Paciente | Validar el formato correcto de DNI (8 dígitos) y RUC (11 dígitos). | Evitar errores en la identificación de pacientes. | - El campo DNI solo acepta 8 dígitos numéricos.<br>- El campo RUC solo acepta 11 dígitos numéricos.<br>- Si el formato es incorrecto, se muestra mensaje de error antes de guardar. |
| **RF-012** | Recepcionista, Laboratorista, Supervisor de Sede | Consultar el historial de órdenes anteriores del paciente. | Conocer el registro de exámenes y resultados previos. | - El sistema muestra una tabla con las órdenes pasadas, fechas, servicios y estado.<br>- Se puede filtrar por rango de fechas o tipo de examen.<br>- Los resultados se cargan sin recargar la página. |
| **RF-013** | Paciente | Validar que DNI/RUC, nombres y apellidos sean obligatorios en el registro. | Garantizar la integridad mínima de los datos del paciente. | - El sistema no permite guardar si los campos obligatorios están vacíos.<br>- Se muestra un mensaje indicando los campos faltantes.<br>- Los campos obligatorios se marcan visualmente con asterisco o color. |
| **RF-014** | Recepcionista, Supervisor de Sede | Identificar y resaltar pacientes recurrentes. | Facilitar el reconocimiento de pacientes frecuentes. | - El sistema marca visualmente (ícono o color) a los pacientes con más de una orden registrada.<br>- Se puede filtrar la lista para mostrar solo recurrentes.<br>- El conteo de visitas se actualiza automáticamente. |
| **RF-015** | Administrador General, Supervisor de Sede | Exportar el listado de pacientes a formato Excel. | Generar reportes o respaldos externos de los registros. | - Se incluye botón “Exportar a Excel” en la vista de pacientes.<br>- El archivo exportado contiene columnas: DNI/RUC, nombres, teléfono, email, dirección, fecha de registro.<br>- La exportación respeta los filtros aplicados.<br>- Solo usuarios con permisos pueden ejecutar esta acción. |

## Módulo de Catálogo de Servicios

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-016** | Administrador General | Crear, modificar y desactivar servicios o exámenes del catálogo. | Mantener actualizado el catálogo de servicios disponibles. | - El sistema permite crear nuevos servicios ingresando código, nombre, categoría y precio.<br>- Se pueden modificar los datos existentes de un servicio.<br>- Los servicios pueden desactivarse sin ser eliminados.<br>- Se registra la fecha y el usuario que realiza cada acción.<br>- Solo el Administrador General puede realizar estas operaciones. |
| **RF-017** | Paciente/ Recepcionista | Visualizar el catálogo de servicios | Consultar fácilmente los servicios disponibles antes de registrarlos en una orden. | - Se muestran únicamente los servicios activos en una tabla con código, nombre, categoría y precio.<br>- Se permite ordenar los resultados por columnas.<br>- La vista se actualiza dinámicamente sin recargar la página. |
| **RF-018** | Paciente/ Recepcionista | Buscar servicios rápidamente | Localizar rápidamente un servicio específico. | - Los resultados se muestran en tiempo real mientras se escribe.<br>- La búsqueda permite coincidencias parciales por código o nombre. |
| **RF-019** | Administrador General | Organizar los servicios por categorías (hematología, bioquímica, etc.). | Facilitar la navegación en el catálogo | - Se permite definir una lista de categorías configurables (ej. hematología, bioquímica, etc.).<br>- Cada servicio puede asociarse a una categoría.<br>- Se muestran los servicios agrupados por categoría en el catálogo.<br>- Solo el Administrador General puede crear o modificar categorías. |
| **RF-020** | Administrador General | Actualizar los precios de los servicios. | Mantener actualizada la información económica del catálogo. | - Se permite editar el precio de los servicios existentes.<br>- Se registra la fecha, hora y usuario responsable del cambio.<br>- Se notifica automáticamente al Supervisor de Sede sobre la actualización.<br>- Solo el Administrador General puede modificar precios. |
| **RF-021** | Supervisor de Sede | Activar o desactivar servicios sin eliminarlos. | Controlar la disponibilidad temporal de los servicios. | - Se permite cambiar el estado de un servicio entre activo e inactivo.<br>- Los servicios inactivos no se muestran en el catálogo público.<br>- Se conserva un historial de los cambios de estado realizados.<br>- Solo usuarios con rol de Administrador pueden ejecutar esta acción. |
| **RF-022** | Administrador General | Consultar el historial de cambios de precios. | Mantener trazabilidad de las modificaciones económicas. | - Se muestra un historial cronológico con la fecha, precio anterior, precio nuevo y usuario responsable.<br>- Se permite filtrar el historial por servicio o rango de fechas.<br>- Solo usuarios con rol de Administrador pueden ejecutar esta acción. |

## Módulo de Registro de Órdenes

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-023** | Recepcionista | Crear órdenes de servicio | Registrar solicitudes de análisis de pacientes. | - Se permite buscar un paciente existente o registrar uno nuevo.<br>- El sistema genera automáticamente un número de orden al guardar.<br>- Se registra el usuario, fecha y hora de creación. |
| **RF-024** | Recepcionista | Agregar múltiples servicios a una orden | Atender solicitudes que pueden contener varios análisis. | - Permite seleccionar múltiples servicios desde el catálogo.<br>- Se muestran los precios individuales y el subtotal acumulado.<br>- Se pueden eliminar servicios antes de guardar la orden. |
| **RF-025** | Recepcionista | Calcular automáticamente los montos | Evitar errores en cálculos manuales. | - El sistema calcula automáticamente el subtotal, el IGV (18%) y el total.<br>- Se muestran los montos antes de confirmar el registro de la orden.<br>- Los cálculos se actualizan al aplicar descuentos o modificar servicios. |
| **RF-026** | Recepcionista | Registrar método de pago | Documentar correctamente las transacciones económicas. | - Se permite seleccionar el método de pago: Efectivo, Tarjeta, Transferencia o Yape/Plin.<br>- Se asocia el pago con la fecha, usuario y monto correspondiente. |
| **RF-027** | Recepcionista | Asignar números de orden únicos | Evitar equivocaciones por identificación de cada orden. | - El sistema genera automáticamente una secuencia de numeración por sede.<br>- Se garantiza que no existan números duplicados.<br>- El número se muestra al confirmar el guardado de la orden. |
| **RF-028** | Recepcionista | Tener un formato estándar para los números de orden | Estandarizar la identificación de órdenes. | - El sistema aplica el formato SEDE-AAAA-NNNNNN (ej. LIM01-2025-000123).<br>- La numeración se reinicia automáticamente al iniciar un nuevo año.<br>- Se valida el formato antes de registrar la orden. |
| **RF-029** | Supervisor de Sede | Aplicar descuentos en órdenes | Ajustar precios según promociones o convenios. | - Se permite aplicar descuentos porcentuales o por monto fijo.<br>- Se muestra el monto descontado y el total actualizado.<br>- Se registra el usuario, fecha y motivo del descuento.<br>- Solo los usuarios autorizados pueden realizar esta acción. |
| **RF-030** | Recepcionista | Validar orden antes de guardar | Evitar el registro de órdenes vacías. | - El sistema verifica que exista al menos un servicio seleccionado.<br>- Se muestra un mensaje de advertencia si no se cumple la condición.<br>- No se permite guardar la orden hasta que se seleccione al menos un servicio. |
| **RF-031** | Recepcionista | Agregar observaciones a la orden | Registrar información complementaria del pedido. | - Se incluye un campo de texto libre para ingresar observaciones.<br>- Las notas se guardan junto con la orden.<br>- Las observaciones se muestran en el detalle de la orden y en los reportes. |
| **RF-032** | Recepcionista | Ver el estado de órdenes | Controlar el flujo operativo de cada orden. | - El sistema asigna el estado “Registrada” por defecto al crear la orden.<br>- Se permite cambiar el estado a “En Proceso”, “Completada” o “Anulada”.<br>- Se registra la fecha, hora y usuario en cada cambio de estado.<br>- El estado actual se muestra visualmente en la interfaz. |
| **RF-033** | Supervisor de Sede | Anular órdenes con justificación | Cancelar órdenes con trazabilidad. | - Solo usuarios autorizados pueden anular órdenes.<br>- Se solicita un motivo obligatorio antes de anular.<br>- Se registra la fecha, usuario y justificación del cambio.<br>- El sistema actualiza el estado de la orden a “Anulada”. |
| **RF-034** | Supervisor de Sede | Que el sistema muestre un listado de órdenes filtrable por estado, paciente o fecha. | Administrar fácilmente las órdenes registradas. | - Se muestra una tabla con número de orden, paciente, estado, total y fecha.<br>- Se permite filtrar los resultados por estado, paciente y rango de fechas.<br>- Se pueden ordenar las columnas según preferencia.<br>- La información se actualiza sin necesidad de recargar la página. |
| **RF-035** | Supervisor de Sede | Que el sistema muestre el detalle completo de una orden seleccionada. | Revisar toda la información de una orden específica. | - Se muestran los datos del paciente, servicios incluidos, precios, método de pago, estado y observaciones.<br>- Se permite imprimir o exportar el detalle de la orden.<br>- Se incluye una opción para regresar al listado general. |

## Módulo de Facturación Electrónica

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-036** | Administrador General | Emitir una boleta electrónica al registrar una orden para un paciente natural | Cumplir con las obligaciones tributarias ante SUNAT y entregar un comprobante válido al paciente. | - El sistema genera automáticamente una boleta electrónica al confirmar la orden.<br>- La boleta incluye número de serie, fecha, monto total e IGV.<br>- Se emite únicamente cuando el paciente no proporciona RUC.<br>- El comprobante se envía al paciente por email de forma inmediata. |
| **RF-037** | Administrador General | Emitir una factura electrónica al registrar una orden para un cliente con RUC (empresa o persona jurídica). | Garantizar que el cliente pueda usar el comprobante para fines fiscales y contables. | - El sistema solicita RUC, razón social y dirección fiscal antes de emitir la factura.<br>- Valida que el RUC tenga 11 dígitos y esté activo en SUNAT (si aplica).<br>- La factura se genera con los datos fiscales completos y se asocia a la orden.<br>- Se emite solo si el cliente es identificado como facturable. |
| **RF-038** | Administrador General | Seleccionar automáticamente el tipo de comprobante (boleta o factura) según el tipo de cliente. | Agilizar el proceso de facturación sin errores manuales. | - Si el paciente tiene RUC registrado, el sistema propone factura; si solo tiene DNI, propone boleta.<br>- El usuario puede confirmar o ajustar la selección antes de emitir.<br>- No se permite emitir factura sin RUC ni razón social. |
| **RF-039** | Administrador General | Ingresar los datos fiscales obligatorios (RUC, razón social, dirección) al emitir una factura. | Cumplir con los requisitos legales de SUNAT para facturas electrónicas. | - Los campos RUC, razón social y dirección fiscal son obligatorios para facturas.<br>- El sistema valida el formato del RUC (11 dígitos numéricos).<br>- No se permite guardar ni emitir la factura si faltan datos. |
| **RF-040** | Administrador General | Integrar el sistema con SUNAT a través de un PSE (Proveedor de Servicios Electrónicos) o API oficial. | Asegurar que los comprobantes tengan validez legal y se registren correctamente ante la autoridad tributaria. | - El sistema permite configurar credenciales de PSE o conexión directa con SUNAT.<br>- Se valida la conexión durante la configuración.<br>- Todos los comprobantes se envían firmados digitalmente al PSE/SUNAT al emitirse. |
| **RF-041** | Administrador General | Obtener la numeración autorizada por SUNAT para boletas y facturas. | Evitar duplicados y garantizar secuencias válidas según la normativa. | - El sistema consulta y utiliza la numeración asignada por SUNAT o el PSE.<br>- No permite emitir comprobantes fuera de la numeración autorizada.<br>- La numeración se gestiona por tipo de comprobante y sede. |
| **RF-042** | Recepcionista | Generar un archivo PDF del comprobante con el formato oficial de SUNAT. | Entregar al paciente un documento legible, impreso o descargable, con validez legal. | - El PDF incluye logo de la empresa, datos fiscales, desglose de servicios, IGV y total.<br>- Cumple con el diseño establecido por SUNAT.<br>- Se genera automáticamente tras la emisión exitosa. |
| **RF-043** | Recepcionista | Generar un archivo XML firmado digitalmente según el estándar de SUNAT. | Cumplir con el requisito técnico de SUNAT para comprobantes electrónicos. | - El XML se genera con la estructura UBL 2.1 o versión vigente.<br>- Incluye firma digital con certificado del PSE o clave SOL.<br>- Se adjunta al email del comprobante y está disponible para descarga. |
| **RF-044** | Recepcionista | Validar la Constancia de Recepción (CDR) emitida por SUNAT antes de confirmar la emisión. | Asegurar que el comprobante fue aceptado por SUNAT y evitar errores no detectados. | - Tras enviar el XML, el sistema consulta la CDR.<br>- Si la CDR indica rechazo, se cancela la emisión y se notifica al usuario.<br>- Solo se marca el comprobante como 'emitido' si la CDR es aceptada. |
| **RF-045** | Administrador General | Anular un comprobante mediante una nota de crédito. | Corregir errores en comprobantes ya emitidos, cumpliendo con la normativa tributaria. | - Solo usuarios autorizados pueden generar notas de crédito.<br>- El sistema vincula la nota al comprobante original.<br>- Se registra motivo, fecha, usuario y se notifica al contador.<br>- No se permite eliminar el comprobante original. |
| **RF-046** | Administrador General | Consultar comprobantes emitidos por número, fecha o cliente. | Facilitar la búsqueda y verificación de comprobantes para atención al cliente o auditoría. | - La búsqueda permite filtrar por número de comprobante, rango de fechas, DNI/RUC o nombre del cliente.<br>- Los resultados muestran tipo, fecha, monto, estado (aceptado/rechazado) y enlace a PDF/XML.<br>- La vista respeta los permisos por rol. |
| **RF-047** | Administrador General | Reenviar un comprobante por email al paciente. | Atender solicitudes de reenvío sin necesidad de volver a emitir. | - Desde la consulta de comprobantes, se muestra un botón 'Reenviar por email'.<br>- El sistema usa la plantilla HTML configurada.<br>- Adjunta PDF y XML del comprobante original.<br>- Registra el reenvío en el historial. |
| **RF-048** | Administrador General | Descargar los archivos PDF y XML de un comprobante emitido. | Permitir el acceso a los formatos oficiales para impresión, contabilidad o respaldo. | - En la vista de detalle del comprobante, hay botones para descargar PDF y XML.<br>- No se requiere autenticación adicional si ya se está en sesión autorizada.<br>- Los archivos descargados son idénticos a los enviados a SUNAT. |

## Módulo de Notificaciones

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-049** | Recepcionista | Que el sistema envíe automáticamente un email al paciente con el comprobante (PDF y XML) al registrar una orden. | Garantizar que el paciente reciba su comprobante de forma inmediata y sin intervención manual. | - Tras confirmar la orden y emitir el comprobante, el sistema envía un email automático al paciente.<br>- El correo incluye los archivos PDF y XML del comprobante.<br>- Se utiliza la dirección de email registrada del paciente.<br>- Si el envío falla, se registra en el historial y se permite reenviar. |
| **RF-050** | Recepcionista | Que el sistema envíe un mensaje por WhatsApp con un enlace para descargar el comprobante. | Ofrecer una alternativa rápida y familiar para pacientes que prefieren comunicarse por WhatsApp. | - El sistema envía un mensaje a través de la API de WhatsApp Business (o servicio integrado) al número del paciente.<br>- El mensaje incluye un enlace seguro y temporal para acceder al PDF del comprobante.<br>- Solo se envía si el paciente tiene número de WhatsApp registrado.<br>- El enlace es válido por 72 horas. |
| **RF-051** | Administrador General | Gestionar plantillas HTML profesionales para los correos electrónicos del sistema. | Asegurar una comunicación institucional coherente, clara y con identidad de marca. | - El sistema permite crear, editar y activar plantillas de email desde la configuración.<br>- Las plantillas incluyen logo, colores corporativos y secciones editables (saludo, cuerpo, firma).<br>- Se aplican automáticamente a todos los correos de comprobantes y notificaciones.<br>- Soporta variables dinámicas como {nombre}, {nro_comprobante}, {enlace_descarga}. |
| **RF-052** | Supervisor de Sede | Recibir notificaciones automáticas de alertas (por email y SMS) cuando se detecten discrepancias en conciliación o errores críticos. | Actuar rápidamente ante situaciones que afecten la integridad financiera o operativa. | - El sistema envía una alerta inmediata al supervisor cuando se detecta una discrepancia (ej.: orden sin comprobante, diferencia en caja).<br>- La notificación incluye tipo de alerta, sede, fecha y acción recomendada.<br>- Se envía por email y SMS si está configurado.<br>- Las alertas se generan en tiempo real durante la conciliación o cierre de caja. |
| **RF-053** | Administrador General | Configurar los destinatarios de las notificaciones de alertas (emails de supervisores, celulares, etc.). | Asegurar que las alertas lleguen a las personas correctas según la sede o rol. | - Desde la configuración, el administrador puede asignar uno o más correos y números de teléfono por sede para recibir alertas.<br>- Los cambios se aplican inmediatamente.<br>- Se valida el formato del email y número de celular.<br>- Solo el Administrador General puede realizar esta configuración. |
| **RF-054** | Administrador General | Consultar un historial de todas las notificaciones enviadas (éxitos y fallos). | Auditar el flujo de comunicaciones y resolver problemas de entrega. | - El sistema registra cada notificación: tipo, destinatario, fecha, estado (enviado/fallido) y contenido resumido.<br>- El historial es accesible desde el módulo de notificaciones.<br>- Permite filtrar por rango de fechas, tipo de notificación o estado.<br>- Los registros se conservan por al menos 12 meses. |
| **RF-055** | Recepcionista | Reenviar notificaciones fallidas o solicitadas nuevamente por el paciente. | Garantizar que el paciente o el supervisor reciba la información, incluso si hubo un fallo inicial. | - Desde el historial de notificaciones, se muestra un botón 'Reenviar' para los registros fallidos o solicitados.<br>- Al reenviar, se usa la plantilla actual y los datos más recientes.<br>- El paciente recibe el comprobante actualizado (PDF/XML) si aplica.<br>- Cada reenvío queda registrado en el historial con marca de 'reenvío manual'. |

## Módulo de Conciliación

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-056** | Administrador General | Que el sistema ejecute una conciliación automática diaria al cierre del día. | Garantizar que todas las operaciones financieras estén balanceadas. | La conciliación debe ejecutarse automáticamente al final del día según la hora configurada y generar un reporte de resultados. |
| **RF-057** | Contador | Comparar las órdenes registradas, comprobantes emitidos y pagos recibidos. | Detectar diferencias entre ventas y facturación. | El sistema debe generar una tabla comparativa que muestre coincidencias y discrepancias entre las fuentes de datos. |
| **RF-058** | Contador | Identificar y reportar diferencias automáticamente. | Corregir errores antes del cierre diario. | El sistema debe resaltar las discrepancias detectadas y enviar alertas al supervisor y al administrador. |
| **RF-059** | Supervisor de Sede | Generar un reporte de cierre de caja por sede y método de pago. | Verificar los ingresos diarios y realizar arqueos. | El sistema debe mostrar los totales por método de pago y permitir exportar el reporte a PDF o Excel. |
| **RF-060** | Contador | Calcular el efectivo esperado versus el efectivo registrado. | Detectar faltantes o sobrantes de caja. | El sistema debe comparar el total registrado por el recepcionista con el total esperado del sistema. |
| **RF-061** | Supervisor de Sede | Recibir alertas inmediatas cuando existan diferencias en conciliación. | Tomar medidas correctivas rápidamente. | El sistema debe enviar notificación por email y/o SMS al detectar una discrepancia. |
| **RF-062** | Administrador General | Consultar el historial de cierres de caja diarios. | Revisar auditorías pasadas o validar correcciones. | El sistema debe listar los cierres anteriores con fecha, usuario responsable y estado (cerrado, reabierto). |
| **RF-063** | Administrador General | Reabrir un cierre de caja para realizar correcciones. | Permitir ajustes contables cuando se identifiquen errores. | Solo el administrador podrá reabrir cierres con una justificación registrada. |
| **RF-064** | Contador | Exportar el reporte de cierre a PDF o Excel. | Archivar los cierres y compartirlos con otras áreas. | El sistema debe permitir la exportación completa del reporte con firma digital y formato estándar. |

## Módulo de Integración con Laboratorio

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-065** | Laboratorista | Que el sistema sincronice automáticamente las órdenes con el sistema del laboratorio. | Evitar registros manuales duplicados. | La sincronización debe ejecutarse automáticamente al registrar o actualizar una orden. |
| **RF-066** | Laboratorista | Enviar datos de la orden como paciente, servicios, fecha y sede. | Procesar correctamente las muestras en el laboratorio. | El sistema debe enviar los datos completos requeridos por el sistema de laboratorio o API. |
| **RF-067** | Administrador General | Integrar el sistema vía API REST o exportación de archivo. | Asegurar compatibilidad con diferentes sistemas de laboratorio. | La integración debe permitir configuración de endpoint o exportación en formato estándar (JSON/XML/CSV). |
| **RF-068** | Laboratorista | Reintentar la sincronización automáticamente si falla. | Garantizar que no se pierdan datos por fallos temporales. | El sistema debe ejecutar hasta 3 reintentos automáticos y registrar los resultados. |
| **RF-069** | Supervisor de Sede | Consultar el log de sincronizaciones exitosas y fallidas. | Monitorear la comunicación entre sistemas. | El log debe mostrar fecha, hora, estado, usuario y detalles del error si existiera. |
| **RF-070** | Laboratorista | Forzar la sincronización manual de una orden específica. | Resolver casos donde la sincronización automática falle. | Debe existir un botón o acción que permita reenviar manualmente una orden pendiente de sincronización. |

## Módulo de Reportes y Dashboard

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-071** | Administrador General | Visualizar un dashboard principal con indicadores clave en tiempo real. | Tomar decisiones rápidas sobre las operaciones del laboratorio. | - El sistema muestra KPIs como número de órdenes, ventas totales y estado de conciliación.<br>- Los datos se actualizan automáticamente sin recargar la página.<br>- El dashboard está accesible solo para roles con permisos (Administrador, Supervisor). |
| **RF-072** | Supervisor de Sede | Ver el número de órdenes del día clasificadas por estado. | Controlar el flujo de trabajo diario. | - El dashboard muestra las órdenes en los estados: Registrada, En proceso, Completada, Anulada.<br>- Se actualiza en tiempo real.<br>- Permite filtrar por sede. |
| **RF-073** | Administrador General | Ver las ventas del día por sede. | Evaluar el desempeño comercial diario. | - El sistema muestra ventas totales por sede.<br>- Se diferencia el total con IGV y sin IGV. |
| **RF-074** | Supervisor de Sede | Generar reportes de órdenes por fecha, sede y estado. | Monitorear la productividad del personal. | - El sistema permite seleccionar rangos de fecha, estado y sede.<br>- Muestra listado detallado con totales. |
| **RF-075** | Contador | Generar reportes de ventas por periodo y sede. | Conciliar la información financiera. | - El reporte incluye fecha, monto total, impuestos, sede y recepcionista.<br>- Permite filtrar por mes o trimestre.<br>- El formato es compatible con conciliación contable. |
| **RF-076** | Administrador General | Ver los servicios más solicitados. | Identificar los exámenes con mayor demanda. | - El sistema lista los 10 servicios más vendidos por periodo.<br>- Muestra cantidad, ingresos generados y porcentaje de participación.<br>- Incluye gráficos para una mejor visualización. |
| **RF-077** | Contador | Ver reportes de ventas por método de pago | Verificar la distribución de ingresos por tipo de cobro. | - El sistema muestra resumen por Tarjeta, Transferencia, Yape/Plin.<br>- Permite exportar y filtrar por sede y fecha.<br>- Incluye totales y porcentajes. |
| **RF-078** | Supervisor de Sede | Ver un reporte de pacientes nuevos y recurrentes | Evaluar la fidelización de clientes. | - El reporte distingue pacientes nuevos (primera visita) y recurrentes (con historial).<br>- Permite seleccionar rango de fechas.<br>- Incluye gráfico comparativo. |
| **RF-079** | Administrador General | Comparar las ventas mensuales entre periodos. | Evaluar el crecimiento del laboratorio. | - El sistema muestra gráfico de líneas o barras comparando las ventas de los últimos 12 meses.<br>- Permite exportar el comparativo.<br>- Se actualiza automáticamente. |
| **RF-080** | Supervisor de Sede | Aplicar filtros dinámicos en los reportes. | Obtener información específica de manera rápida. | - Los reportes permiten filtrar por fecha, sede y recepcionista.<br>- Los filtros se aplican sin recargar la página.<br>- Se puede limpiar o restablecer los filtros. |
| **RF-081** | Administrador General | Exportar los reportes a PDF | Compartirlos con otras áreas o archivarlos. | - Los reportes se exportan con formato legible y logos institucionales.<br>- La exportación conserva filtros aplicados.<br>- Compatible con PDF. |
| **RF-082** | Administrador General | Visualizar gráficos estadísticos en los reportes. | Analizar las tendencias de manera visual. | - El sistema genera gráficos de barras, líneas o pastel según el tipo de reporte.<br>- Los gráficos son interactivos.<br>- Se actualizan al aplicar filtros. |

## Módulo de Configuración

| Requerimiento | Como | Quiero | Para | Criterios de aceptación |
| :--- | :--- | :--- | :--- | :--- |
| **RF-083** | Administrador General | Gestionar las sedes del laboratorio. | Mantener actualizada la información de contacto y ubicación. | - Permite crear, editar y eliminar sedes.<br>- Cada sede tiene nombre, dirección, teléfono y código identificador.<br>- No permite ingresar duplicados. |
| **RF-084** | Administrador General | Configurar el porcentaje de IGV | Garantizar el cálculo correcto de los montos facturados. | - El sistema permite definir el porcentaje vigente de IGV.<br>- Los cambios se reflejan automáticamente en las órdenes.<br>- Solo el administrador puede modificarlo. |
| **RF-085** | Administrador General | Registrar los datos de la empresa (RUC, razón social, logo) | Incluirlos en los comprobantes y reportes. | - Se registran los campos RUC, razón social, dirección y logo.<br>- La información se muestra en facturas, boletas y reportes oficiales.<br>- Solo accesible a administradores. |
| **RF-086** | Administrador General | Configurar las credenciales SUNAT o PSE. | Habilitar la emisión de comprobantes electrónicos. | - Permite ingresar usuario, clave SOL y credenciales del PSE.<br>- El sistema valida la conexión con SUNAT.<br>- Solo el administrador puede modificarlo. |
| **RF-087** | Administrador General | Configurar el servidor de correo SMTP. | Enviar notificaciones automáticas y comprobantes por email. | - Permite definir host, puerto, usuario y contraseña SMTP.<br>- Se puede probar el envío de un correo de prueba.<br>- El sistema encripta la contraseña. |
| **RF-088** | Supervisor de Sede | Ajustar parámetros locales del sistema. | Definir hora de cierre automático y duración de sesiones activas. | - El sistema permite modificar hora de cierre diario y tiempo máximo de sesión.<br>- Los cambios solo afectan a la sede configurada.<br>- Se registra el historial de cambios. |
| **RF-089** | Administrador General | Tener backups automáticos de la base de datos. | Proteger la información ante fallos. | - El sistema genera copias automáticas diarias en horario programado.<br>- Permite definir la ruta o almacenamiento en la nube.<br>- Se notifican errores de respaldo. |
| **RF-090** | Administrador General | Restaurar un backup del sistema | Recuperar información en caso de pérdida o error. | - Permite seleccionar un archivo de backup y restaurar.<br>- Muestra confirmación antes de proceder.<br>- Solo usuarios con rol de Administrador pueden ejecutar esta acción. |

## Requerimientos No Funcionales

| Módulo | ID | Requerimiento | Métrica | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Rendimiento** | RNF-001 | Tiempo de respuesta | < 2 segundos | El sistema debe responder a solicitudes del usuario en menos de 2 segundos para operaciones normales |
| | RNF-002 | Búsqueda de pacientes | < 1 segundo | La búsqueda de pacientes debe retornar resultados en menos de 1 segundo |
| | RNF-003 | Emisión de comprobantes | < 5 segundos | La emisión de comprobantes electrónicos debe completarse en menos de 5 segundos |
| | RNF-004 | Concurrencia | 50 usuarios | El sistema debe soportar al menos 50 usuarios simultáneos (8 sedes × 6-7 usuarios) |
| | RNF-005 | Procesamiento de órdenes | 500 órdenes/día | El sistema debe procesar sin degradación hasta 500 órdenes diarias |
| | RNF-006 | Carga de dashboard | < 3 segundos | El dashboard debe cargar en menos de 3 segundos |
| | RNF-007 | Procesamiento asíncrono | No bloquea UI | Las operaciones asíncronas (notificaciones, sincronización) no deben bloquear la interfaz |
| **Disponibilidad y Confiabilidad** | RNF-008 | Disponibilidad | 99% uptime | El sistema debe estar disponible al menos 99% del tiempo (máximo 3.65 días caídos/año) |
| | RNF-009 | Horario crítico | 99.9% (7am-7pm) | En horario de atención (7am-7pm) disponibilidad debe ser 99.9% |
| | RNF-010 | Recuperación ante fallos | < 15 minutos | El sistema debe recuperarse de fallos en menos de 15 minutos |
| | RNF-011 | Backup automático | Diario | El sistema debe realizar backup automático diario |
| | RNF-012 | Retención de backups | 30 días | Los backups deben mantenerse por 30 días mínimo |
| | RNF-013 | Tolerancia a fallos | Reintentos automáticos | El sistema debe reintentar operaciones fallidas automáticamente (max 3 intentos) |
| | RNF-014 | Cola de mensajes | Persistencia | Los eventos en RabbitMQ deben ser persistentes para no perder datos |
| **Seguridad** | RNF-015 | Autenticación segura | | El sistema debe implementar autenticación mediante JWT con expiración de tokens |
| | RNF-016 | Contraseñas encriptadas | | Las contraseñas deben almacenarse encriptadas con bcrypt o similar (min 10 rounds) |
| | RNF-017 | HTTPS | | Todas las comunicaciones deben ser mediante HTTPS/TLS 1.2+ |
| | RNF-018 | Control de acceso | | El sistema debe implementar RBAC (Role-Based Access Control) |
| | RNF-019 | Sesiones | | Las sesiones deben expirar tras 30 minutos de inactividad |
| | RNF-020 | Registro de auditoría | | El sistema debe registrar todas las operaciones críticas (quién, qué, cuándo) |
| | RNF-021 | Protección CSRF | | El sistema debe proteger contra ataques CSRF |
| | RNF-022 | Protección XSS | | El sistema debe sanitizar inputs para prevenir XSS |
| | RNF-023 | SQL Injection | | El sistema debe usar consultas parametrizadas para prevenir SQL Injection |
| | RNF-024 | Rate Limiting | | El sistema debe limitar peticiones a 100 requests/minuto por usuario |
| | RNF-025 | Firma digital | | Los comprobantes XML deben estar firmados digitalmente |
| **Usabilidad** | RNF-026 | Interfaz intuitiva | | La interfaz debe ser clara y fácil de usar, sin requerir manual extenso |
| | RNF-027 | Navegación | | El usuario debe poder completar tareas principales en máximo 5 clics |
| | RNF-028 | Mensajes de error | | Los mensajes de error deben ser claros y orientar al usuario sobre cómo resolverlos |
| | RNF-029 | Validación en tiempo real | | El sistema debe validar campos en tiempo real (feedback inmediato) |
| | RNF-030 | Responsive design | | La interfaz debe adaptarse a pantallas de escritorio (1366×768 mínimo) |
| | RNF-031 | Accesibilidad | | El sistema debe cumplir estándares WCAG 2.1 nivel AA |
| | RNF-032 | Idioma | | El sistema debe estar en español peruano |
| | RNF-033 | Ayuda contextual | | El sistema debe incluir tooltips y ayuda contextual en formularios complejos |
| | RNF-034 | Autocompletado | | Los campos de búsqueda deben incluir autocompletado |
| **Mantenibilidad** | RNF-035 | Código limpio | | El código debe seguir estándares de calidad y buenas prácticas (PEP8, ESLint) |
| | RNF-036 | Documentación técnica | | El sistema debe incluir documentación técnica completa (README, API docs) |
| | RNF-037 | Arquitectura modular | | Los servicios deben estar desacoplados y ser independientes |
| | RNF-038 | Tests automatizados | | El código debe tener cobertura de tests unitarios de al menos 70% |
| | RNF-039 | Logs estructurados | | El sistema debe generar logs estructurados con niveles (INFO, WARN, ERROR) |
| | RNF-040 | Monitoreo | | El sistema debe incluir endpoints de health check para monitoreo |
| | RNF-041 | Versionamiento | | El código debe versionarse con Git siguiendo GitFlow |
| **Escalabilidad** | RNF-042 | Escalabilidad horizontal | | Los servicios deben poder escalarse agregando más instancias |
| | RNF-043 | Crecimiento de datos | | El sistema debe soportar crecimiento de datos hasta 1 millón de órdenes |
| | RNF-044 | Nuevas sedes | | El sistema debe permitir agregar nuevas sedes sin cambios en código |
| | RNF-045 | Cache | | El sistema debe implementar cache para consultas frecuentes (catálogo, configuración) |
| **Compatibilidad** | RNF-046 | Navegadores | | El sistema debe funcionar en Chrome 90+, Firefox 88+, Edge 90+ |
| | RNF-047 | Resolución mínima | | El sistema debe funcionar en resolución mínima 1366×768 |
| | RNF-048 | API REST | | Las APIs deben seguir estándares REST con respuestas JSON |
| | RNF-049 | Integración SUNAT | | El sistema debe ser compatible con especificaciones SUNAT vigentes |
| **Portabilidad** | RNF-050 | Contenedores | | El sistema debe desplegarse usando Docker |
| | RNF-051 | Base de datos | | El sistema debe funcionar con PostgreSQL 12+ |
| | RNF-052 | Sistema operativo | | El sistema debe poder ejecutarse en Linux (Ubuntu 20.04+) |
| | RNF-053 | Cloud ready | | El sistema debe poder desplegarse en AWS, Google Cloud o Azure |
| **Regulatorios y Legales** | RNF-054 | Normativa SUNAT | | El sistema debe cumplir con regulaciones SUNAT para facturación electrónica |
| | RNF-055 | Ley de protección de datos | | El sistema debe cumplir con Ley N° 29733 (Protección de Datos Personales - Perú) |
| | RNF-056 | Retención de datos | | Los datos deben retenerse por 5 años según normativa contable |
| | RNF-057 | Libros electrónicos | | El sistema debe generar registros compatibles con Libros Electrónicos (PLE SUNAT) |
```
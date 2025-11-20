Módulo de Gestión de Usuarios y Autenticación
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-001
Paciente
Iniciar sesión mediante usuario y contraseña.
Acceder de forma segura al sistema.
- El sistema valida usuario y contraseña.
- Solo usuarios activos pueden acceder.
- Se muestra mensaje de error si las credenciales son incorrectas.
- Tras iniciar sesión, se redirige al panel según su rol.



RF-002
Administrador General
Gestionar los roles de los usuarios (Administrador, Recepcionista, Supervisor, Laboratorista).
Controlar los permisos y accesos dentro del sistema.
- El sistema permite asignar y cambiar roles de usuarios existentes.
- Solo el Administrador General puede modificar roles.
- Cada rol tiene acceso restringido a sus funciones.
- Los cambios de rol se registran con fecha y usuario responsable.



RF-003
Paciente
Cerrar sesión de forma segura.
Finalizar la sesión actual y proteger la cuenta del usuario.
- El sistema cierra la sesión actual al solicitarlo.
- Se elimina la sesión activa del navegador.
- Se redirige al formulario de inicio de sesión.



RF-004
Paciente
Recuperar su contraseña mediante correo electrónico.
Restablecer el acceso en caso de olvido o pérdida de contraseña.
- El usuario puede solicitar recuperación ingresando su email registrado.
- El sistema envía un enlace temporal para restablecer la contraseña.
- El enlace expira después de un tiempo determinado.
- La nueva contraseña debe cumplir con las políticas de seguridad.



RF-005
Administrador General
Crear, modificar y desactivar usuarios del sistema.
Mantener actualizada la base de usuarios.
- El sistema permite registrar nuevos usuarios con nombre, email, rol y sede.
- Se pueden editar los datos existentes.
- Los usuarios pueden desactivarse sin ser eliminados.
- Se registra la fecha y el usuario que realiza cada acción.



RF-006
Administrador General
Asignar una sede específica a cada usuario.
Organizar correctamente el personal según su ubicación.
- Durante la creación o edición de usuarios, se debe asignar una sede.
- Un usuario solo puede pertenecer a una sede a la vez.
- Los usuarios pueden filtrarse por sede.
- Solo el Administrador General puede realizar esta asignación.



RF-007
Paciente
Ver y actualizar su información de perfil.
Mantener actualizados sus datos personales.
- El usuario puede acceder a su perfil desde el menú principal.
- Puede actualizar información básica (nombre, email, contraseña).
- Los cambios se guardan inmediatamente y se confirman al usuario.
- El sistema valida los datos antes de actualizar.



Módulo de Gestión de Pacientes
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-008
Administrador General, Recepcionista
Registrar nuevos pacientes con DNI/RUC, nombres, teléfono, email y dirección.
Mantener actualizada la base de datos de pacientes.
- El sistema permite registrar un nuevo paciente ingresando los campos requeridos.
- Se valida que el DNI o RUC no estén duplicados.
- Al guardar, se muestra confirmación del registro exitoso.
- Solo usuarios autorizados pueden realizar el registro.



RF-009
Supervisor de Sede, Recepcionista
Buscar pacientes por DNI, RUC, nombres o apellidos.
Localizar rápidamente la información de un paciente.
- Se dispone de un campo de búsqueda con coincidencias parciales.
- Los resultados se muestran en tiempo real o tras presionar “Buscar”.
- Se puede ordenar y filtrar por tipo de documento o nombre.



RF-010
Administrador General, Recepcionista
Actualizar la información de pacientes existentes.
Corregir o completar datos registrados.
- El sistema permite editar datos personales, contacto y dirección.
- Se registra la fecha y usuario que realizó la modificación.
- No se permiten duplicados de DNI/RUC.
- Se muestra un mensaje de confirmación tras guardar los cambios.



RF-011
Paciente
Validar el formato correcto de DNI (8 dígitos) y RUC (11 dígitos).
Evitar errores en la identificación de pacientes.
- El campo DNI solo acepta 8 dígitos numéricos.
- El campo RUC solo acepta 11 dígitos numéricos.
- Si el formato es incorrecto, se muestra mensaje de error antes de guardar.



RF-012
Recepcionista, Laboratorista, Supervisor de Sede
Consultar el historial de órdenes anteriores del paciente.
Conocer el registro de exámenes y resultados previos.
- El sistema muestra una tabla con las órdenes pasadas, fechas, servicios y estado.
- Se puede filtrar por rango de fechas o tipo de examen.
- Los resultados se cargan sin recargar la página.



RF-013
Paciente
Validar que DNI/RUC, nombres y apellidos sean obligatorios en el registro.
Garantizar la integridad mínima de los datos del paciente.
- El sistema no permite guardar si los campos obligatorios están vacíos.
- Se muestra un mensaje indicando los campos faltantes.
- Los campos obligatorios se marcan visualmente con asterisco o color



RF-014
Recepcionista, Supervisor de Sede
Identificar y resaltar pacientes recurrentes.
Facilitar el reconocimiento de pacientes frecuentes.
- El sistema marca visualmente (ícono o color) a los pacientes con más de una orden registrada.
- Se puede filtrar la lista para mostrar solo recurrentes.
- El conteo de visitas se actualiza automáticamente.



RF-015
Administrador General, Supervisor de Sede
Exportar el listado de pacientes a formato Excel.
Generar reportes o respaldos externos de los registros.
- Se incluye botón “Exportar a Excel” en la vista de pacientes.
- El archivo exportado contiene columnas: DNI/RUC, nombres, teléfono, email, dirección, fecha de registro.
- La exportación respeta los filtros aplicados.
- Solo usuarios con permisos pueden ejecutar esta acción.



Módulo de Catálogo de Servicios
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-016
Administrador General
Crear, modificar y desactivar servicios o exámenes del catálogo.
Mantener actualizado el catálogo de servicios disponibles.
- El sistema permite crear nuevos servicios ingresando código, nombre, categoría y precio.
- Se pueden modificar los datos existentes de un servicio.
- Los servicios pueden desactivarse sin ser eliminados.
- Se registra la fecha y el usuario que realiza cada acción.
- Solo el Administrador General puede realizar estas operaciones.
RF-017
Paciente/ Recepcionista
Visualizar el catálogo de servicios
Consultar fácilmente los servicios disponibles antes de registrarlos en una orden.
- Se muestran únicamente los servicios activos en una tabla con código, nombre, categoría y precio.
- Se permite ordenar los resultados por columnas.
- La vista se actualiza dinámicamente sin recargar la página.
RF-018
Paciente/ Recepcionista
Buscar servicios rápidamente
Localizar rápidamente un servicio específico.
- Los resultados se muestran en tiempo real mientras se escribe.
- La búsqueda permite coincidencias parciales por código o nombre.
RF-019
Administrador General
Organizar los servicios por categorías (hematología, bioquímica, etc.).
Facilitar la navegación en el catálogo
- Se permite definir una lista de categorías configurables (ej. hematología, bioquímica, etc.).
- Cada servicio puede asociarse a una categoría.
- Se muestran los servicios agrupados por categoría en el catálogo.
- Solo el Administrador General puede crear o modificar categorías.
RF-020
Administrador General
Actualizar los precios de los servicios.
Mantener actualizada la información económica del catálogo.
- Se permite editar el precio de los servicios existentes.
- Se registra la fecha, hora y usuario responsable del cambio.
- Se notifica automáticamente al Supervisor de Sede sobre la actualización.
- Solo el Administrador General puede modificar precios.
RF-021
Supervisor de Sede
Activar o desactivar servicios sin eliminarlos.
Controlar la disponibilidad temporal de los servicios.
- Se permite cambiar el estado de un servicio entre activo e inactivo.
- Los servicios inactivos no se muestran en el catálogo público.
- Se conserva un historial de los cambios de estado realizados.
- Solo usuarios con rol de Administrador pueden ejecutar esta acción.
RF-022
Administrador General
Consultar el historial de cambios de precios.
Mantener trazabilidad de las modificaciones económicas.
- Se muestra un historial cronológico con la fecha, precio anterior, precio nuevo y usuario responsable.
- Se permite filtrar el historial por servicio o rango de fechas.
- Solo usuarios con rol de Administrador pueden ejecutar esta acción.
Módulo de Registro de Órdenes
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-023
Recepcionista
Crear órdenes de servicio
Registrar solicitudes de análisis de pacientes.
- Se permite buscar un paciente existente o registrar uno nuevo.
- El sistema genera automáticamente un número de orden al guardar.
- Se registra el usuario, fecha y hora de creación.
RF-024
Recepcionista
Agregar múltiples servicios a una orden
Atender solicitudes que pueden contener varios análisis.
- Permite seleccionar múltiples servicios desde el catálogo.
- Se muestran los precios individuales y el subtotal acumulado.
- Se pueden eliminar servicios antes de guardar la orden.
RF-025
Recepcionista
Calcular automáticamente los montos
Evitar errores en cálculos manuales.
- El sistema calcula automáticamente el subtotal, el IGV (18%) y el total.
- Se muestran los montos antes de confirmar el registro de la orden.
- Los cálculos se actualizan al aplicar descuentos o modificar servicios.
RF-026
Recepcionista
Registrar método de pago
Documentar correctamente las transacciones económicas.
- Se permite seleccionar el método de pago: Efectivo, Tarjeta, Transferencia o Yape/Plin.
- Se asocia el pago con la fecha, usuario y monto correspondiente.
RF-027
Recepcionista
Asignar números de orden únicos
Evitar equivocaciones por identificación de cada orden.
- El sistema genera automáticamente una secuencia de numeración por sede.
- Se garantiza que no existan números duplicados.
- El número se muestra al confirmar el guardado de la orden.
RF-028
Recepcionista
Tener un formato estándar para los números de orden
Estandarizar la identificación de órdenes.
- El sistema aplica el formato SEDE-AAAA-NNNNNN (ej. LIM01-2025-000123).
- La numeración se reinicia automáticamente al iniciar un nuevo año.
- Se valida el formato antes de registrar la orden.
RF-029
Supervisor de Sede
Aplicar descuentos en órdenes
Ajustar precios según promociones o convenios.
- Se permite aplicar descuentos porcentuales o por monto fijo.
- Se muestra el monto descontado y el total actualizado.
- Se registra el usuario, fecha y motivo del descuento.
- Solo los usuarios autorizados pueden realizar esta acción.
RF-030
Recepcionista
Validar orden antes de guardar
Evitar el registro de órdenes vacías.
- El sistema verifica que exista al menos un servicio seleccionado.
- Se muestra un mensaje de advertencia si no se cumple la condición.
- No se permite guardar la orden hasta que se seleccione al menos un servicio.
RF-031
Recepcionista
Agregar observaciones a la orden
Registrar información complementaria del pedido.
- Se incluye un campo de texto libre para ingresar observaciones.
- Las notas se guardan junto con la orden.
- Las observaciones se muestran en el detalle de la orden y en los reportes.
RF-032
Recepcionista
Ver el estado de órdenes
Controlar el flujo operativo de cada orden.
- El sistema asigna el estado “Registrada” por defecto al crear la orden.
- Se permite cambiar el estado a “En Proceso”, “Completada” o “Anulada”.
- Se registra la fecha, hora y usuario en cada cambio de estado.
- El estado actual se muestra visualmente en la interfaz.
RF-033
Supervisor de Sede
Anular órdenes con justificación
Cancelar órdenes con trazabilidad.
- Solo usuarios autorizados pueden anular órdenes.
- Se solicita un motivo obligatorio antes de anular.
- Se registra la fecha, usuario y justificación del cambio.
- El sistema actualiza el estado de la orden a “Anulada”.
RF-034
Supervisor de Sede
Que el sistema muestre un listado de órdenes filtrable por estado, paciente o fecha.
Administrar fácilmente las órdenes registradas.
- Se muestra una tabla con número de orden, paciente, estado, total y fecha.
- Se permite filtrar los resultados por estado, paciente y rango de fechas.
- Se pueden ordenar las columnas según preferencia.
- La información se actualiza sin necesidad de recargar la página.
RF-035
Supervisor de Sede
Que el sistema muestre el detalle completo de una orden seleccionada.
Revisar toda la información de una orden específica.
- Se muestran los datos del paciente, servicios incluidos, precios, método de pago, estado y observaciones.
- Se permite imprimir o exportar el detalle de la orden.
- Se incluye una opción para regresar al listado general.
Módulo de Facturación Electrónica
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-036
Administrador General
Emitir una
boleta electrónica
al registrar una orden para un paciente natural
Cumplir con las obligaciones tributarias ante SUNAT y entregar un comprobante válido al paciente.
- El sistema genera automáticamente una boleta electrónica al confirmar la orden.
- La boleta incluye número de serie, fecha, monto total e IGV.
- Se emite únicamente cuando el paciente no proporciona RUC.
- El comprobante se envía al paciente por email de forma inmediata.
RF-037
Administrador General
Emitir una factura electrónica al registrar una orden para un cliente con RUC (empresa o persona jurídica).
Garantizar que el cliente pueda usar el comprobante para fines fiscales y contables.
- El sistema solicita RUC, razón social y dirección fiscal antes de emitir la factura.
- Valida que el RUC tenga 11 dígitos y esté activo en SUNAT (si aplica)
.- La factura se genera con los datos fiscales completos y se asocia a la orden.
- Se emite solo si el cliente es identificado como facturable.
RF-038
Administrador General
Seleccionar automáticamente el tipo de comprobante (boleta o factura) según el tipo de cliente.
Agilizar el proceso de facturación sin errores manuales.
- Si el paciente tiene RUC registrado, el sistema propone factura; si solo tiene DNI, propone boleta.- El usuario puede confirmar o ajustar la selección antes de emitir.- No se permite emitir factura sin RUC ni razón social.
RF-039
Administrador General
Ingresar los datos fiscales obligatorios (RUC, razón social, dirección) al emitir una factura.
Cumplir con los requisitos legales de SUNAT para facturas electrónicas.
- Los campos RUC, razón social y dirección fiscal son obligatorios para facturas.- El sistema valida el formato del RUC (11 dígitos numéricos).- No se permite guardar ni emitir la factura si faltan datos.
RF-040
Administrador General
Integrar el sistema con SUNAT a través de un PSE (Proveedor de Servicios Electrónicos) o API oficial.
Asegurar que los comprobantes tengan validez legal y se registren correctamente ante la autoridad tributaria.
- El sistema permite configurar credenciales de PSE o conexión directa con SUNAT.- Se valida la conexión durante la configuración.- Todos los comprobantes se envían firmados digitalmente al PSE/SUNAT al emitirse.
RF-041
Administrador General
Obtener la numeración autorizada por SUNAT para boletas y facturas.
Evitar duplicados y garantizar secuencias válidas según la normativa.
- El sistema consulta y utiliza la numeración asignada por SUNAT o el PSE.- No permite emitir comprobantes fuera de la numeración autorizada.- La numeración se gestiona por tipo de comprobante y sede.
RF-042
Recepcionista
Generar un archivo PDF del comprobante con el formato oficial de SUNAT.
Entregar al paciente un documento legible, impreso o descargable, con validez legal.
- El PDF incluye logo de la empresa, datos fiscales, desglose de servicios, IGV y total.- Cumple con el diseño establecido por SUNAT.- Se genera automáticamente tras la emisión exitosa.
RF-043
Recepcionista
Generar un archivo XML firmado digitalmente según el estándar de SUNAT.
Cumplir con el requisito técnico de SUNAT para comprobantes electrónicos.
- El XML se genera con la estructura UBL 2.1 o versión vigente.- Incluye firma digital con certificado del PSE o clave SOL.- Se adjunta al email del comprobante y está disponible para descarga.
RF-044
Recepcionista
Validar la Constancia de Recepción (CDR) emitida por SUNAT antes de confirmar la emisión.
Asegurar que el comprobante fue aceptado por SUNAT y evitar errores no detectados.
- Tras enviar el XML, el sistema consulta la CDR.- Si la CDR indica rechazo, se cancela la emisión y se notifica al usuario.- Solo se marca el comprobante como 'emitido' si la CDR es aceptada.
RF-045
Administrador General
Anular un comprobante mediante una nota de crédito.
Corregir errores en comprobantes ya emitidos, cumpliendo con la normativa tributaria.
- Solo usuarios autorizados pueden generar notas de crédito.- El sistema vincula la nota al comprobante original.- Se registra motivo, fecha, usuario y se notifica al contador.<br>- No se permite eliminar el comprobante original.
RF-046
Administrador General
Consultar comprobantes emitidos por número, fecha o cliente.
Facilitar la búsqueda y verificación de comprobantes para atención al cliente o auditoría.
- La búsqueda permite filtrar por número de comprobante, rango de fechas, DNI/RUC o nombre del cliente.- Los resultados muestran tipo, fecha, monto, estado (aceptado/rechazado) y enlace a PDF/XML.- La vista respeta los permisos por rol.
RF-047
Administrador General
Reenviar un comprobante por email al paciente.
Atender solicitudes de reenvío sin necesidad de volver a emitir.
- Desde la consulta de comprobantes, se muestra un botón 'Reenviar por email'.- El sistema usa la plantilla HTML configurada.- Adjunta PDF y XML del comprobante original.<br>- Registra el reenvío en el historial.
RF-048
Administrador General
Descargar los archivos PDF y XML de un comprobante emitido.
Permitir el acceso a los formatos oficiales para impresión, contabilidad o respaldo.
- En la vista de detalle del comprobante, hay botones para descargar PDF y XML.- No se requiere autenticación adicional si ya se está en sesión autorizada.<- Los archivos descargados son idénticos a los enviados a SUNAT.
Módulo de Notificaciones
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-049
Recepcionista
Que el sistema envíe automáticamente un email al paciente con el comprobante (PDF y XML) al registrar una orden.
Garantizar que el paciente reciba su comprobante de forma inmediata y sin intervención manual.
- Tras confirmar la orden y emitir el comprobante, el sistema envía un email automático al paciente.- El correo incluye los archivos PDF y XML del comprobante.- Se utiliza la dirección de email registrada del paciente.<- Si el envío falla, se registra en el historial y se permite reenviar.
RF-050
Recepcionista
Que el sistema envíe un mensaje por WhatsApp con un enlace para descargar el comprobante.
Ofrecer una alternativa rápida y familiar para pacientes que prefieren comunicarse por WhatsApp.
- El sistema envía un mensaje a través de la API de WhatsApp Business (o servicio integrado) al número del paciente.- El mensaje incluye un enlace seguro y temporal para acceder al PDF del comprobante.- Solo se envía si el paciente tiene número de WhatsApp registrado.- El enlace es válido por 72 horas.
RF-051
Administrador General
Gestionar plantillas HTML profesionales para los correos electrónicos del sistema.
Asegurar una comunicación institucional coherente, clara y con identidad de marca.
- El sistema permite crear, editar y activar plantillas de email desde la configuración.- Las plantillas incluyen logo, colores corporativos y secciones editables (saludo, cuerpo, firma).- Se aplican automáticamente a todos los correos de comprobantes y notificaciones.- Soporta variables dinámicas como {nombre}, {nro_comprobante}, {enlace_descarga}.
RF-052
Supervisor de Sede
Recibir notificaciones automáticas de alertas (por email y SMS) cuando se detecten discrepancias en conciliación o errores críticos.
Actuar rápidamente ante situaciones que afecten la integridad financiera o operativa.
- El sistema envía una alerta inmediata al supervisor cuando se detecta una discrepancia (ej.: orden sin comprobante, diferencia en caja).- La notificación incluye tipo de alerta, sede, fecha y acción recomendada.- Se envía por email y SMS si está configurado.- Las alertas se generan en tiempo real durante la conciliación o cierre de caja.
RF-053
Administrador General
Configurar los destinatarios de las notificaciones de alertas (emails de supervisores, celulares, etc.).
Asegurar que las alertas lleguen a las personas correctas según la sede o rol.
- Desde la configuración, el administrador puede asignar uno o más correos y números de teléfono por sede para recibir alertas.- Los cambios se aplican inmediatamente.- Se valida el formato del email y número de celular.- Solo el Administrador General puede realizar esta configuración.
RF-054
Administrador General
Consultar un historial de todas las notificaciones enviadas (éxitos y fallos).
Auditar el flujo de comunicaciones y resolver problemas de entrega.
- El sistema registra cada notificación: tipo, destinatario, fecha, estado (enviado/fallido) y contenido resumido.- El historial es accesible desde el módulo de notificaciones.- Permite filtrar por rango de fechas, tipo de notificación o estado.- Los registros se conservan por al menos 12 meses.
RF-055
Recepcionista
Reenviar notificaciones fallidas o solicitadas nuevamente por el paciente.
Garantizar que el paciente o el supervisor reciba la información, incluso si hubo un fallo inicial.
- Desde el historial de notificaciones, se muestra un botón 'Reenviar' para los registros fallidos o solicitados.- Al reenviar, se usa la plantilla actual y los datos más recientes.- El paciente recibe el comprobante actualizado (PDF/XML) si aplica.- Cada reenvío queda registrado en el historial con marca de 'reenvío manual'.
Módulo de Conciliación
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-056
Administrador General
Que el sistema ejecute una conciliación automática diaria al cierre del día.
Garantizar que todas las operaciones financieras estén balanceadas.
La conciliación debe ejecutarse automáticamente al final del día según la hora configurada y generar un reporte de resultados.
RF-057
Contador
Comparar las órdenes registradas, comprobantes emitidos y pagos recibidos.
Detectar diferencias entre ventas y facturación.
El sistema debe generar una tabla comparativa que muestre coincidencias y discrepancias entre las fuentes de datos.
RF-058
Contador
Identificar y reportar diferencias automáticamente.
Corregir errores antes del cierre diario.
El sistema debe resaltar las discrepancias detectadas y enviar alertas al supervisor y al administrador.
RF-059
Supervisor de Sede
Generar un reporte de cierre de caja por sede y método de pago.
Verificar los ingresos diarios y realizar arqueos.
El sistema debe mostrar los totales por método de pago y permitir exportar el reporte a PDF o Excel.
RF-060
Contador
Calcular el efectivo esperado versus el efectivo registrado.
Detectar faltantes o sobrantes de caja.
El sistema debe comparar el total registrado por el recepcionista con el total esperado del sistema.
RF-061
Supervisor de Sede
Recibir alertas inmediatas cuando existan diferencias en conciliación.
Tomar medidas correctivas rápidamente.
El sistema debe enviar notificación por email y/o SMS al detectar una discrepancia.
RF-062
Administrador General
Consultar el historial de cierres de caja diarios.
Revisar auditorías pasadas o validar correcciones.
El sistema debe listar los cierres anteriores con fecha, usuario responsable y estado (cerrado, reabierto).
RF-063
Administrador General
Reabrir un cierre de caja para realizar correcciones.
Permitir ajustes contables cuando se identifiquen errores.
Solo el administrador podrá reabrir cierres con una justificación registrada.
RF-064
Contador
Exportar el reporte de cierre a PDF o Excel.
Archivar los cierres y compartirlos con otras áreas.
El sistema debe permitir la exportación completa del reporte con firma digital y formato estándar.
Módulo de Integración con Laboratorio
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-065
Laboratorista
Que el sistema sincronice automáticamente las órdenes con el sistema del laboratorio.
Evitar registros manuales duplicados.
La sincronización debe ejecutarse automáticamente al registrar o actualizar una orden.
RF-066
Laboratorista
Enviar datos de la orden como paciente, servicios, fecha y sede.
Procesar correctamente las muestras en el laboratorio.
El sistema debe enviar los datos completos requeridos por el sistema de laboratorio o API.
RF-067
Administrador General
Integrar el sistema vía API REST o exportación de archivo.
Asegurar compatibilidad con diferentes sistemas de laboratorio.
La integración debe permitir configuración de endpoint o exportación en formato estándar (JSON/XML/CSV).
RF-068
Laboratorista
Reintentar la sincronización automáticamente si falla.
Garantizar que no se pierdan datos por fallos temporales.
El sistema debe ejecutar hasta 3 reintentos automáticos y registrar los resultados.
RF-069
Supervisor de Sede
Consultar el log de sincronizaciones exitosas y fallidas.
Monitorear la comunicación entre sistemas.
El log debe mostrar fecha, hora, estado, usuario y detalles del error si existiera.
RF-070
Laboratorista
Forzar la sincronización manual de una orden específica.
Resolver casos donde la sincronización automática falle.
Debe existir un botón o acción que permita reenviar manualmente una orden pendiente de sincronización.
Módulo de Reportes y Dashboard
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-071
Administrador General
Visualizar un dashboard principal con indicadores clave en tiempo real.
Tomar decisiones rápidas sobre las operaciones del laboratorio.
- El sistema muestra KPIs como número de órdenes, ventas totales y estado de conciliación.
- Los datos se actualizan automáticamente sin recargar la página.
- El dashboard está accesible solo para roles con permisos (Administrador, Supervisor).
RF-072
Supervisor de Sede
Ver el número de órdenes del día clasificadas por estado.
Controlar el flujo de trabajo diario.
- El dashboard muestra las órdenes en los estados: Registrada, En proceso, Completada, Anulada.
- Se actualiza en tiempo real.
- Permite filtrar por sede.
RF-073
Administrador General
Ver las ventas del día por sede.
Evaluar el desempeño comercial diario.
- El sistema muestra ventas totales por sede.
- Se diferencia el total con IGV y sin IGV.
RF-074
Supervisor de Sede
Generar reportes de órdenes por fecha, sede y estado.
Monitorear la productividad del personal.
- El sistema permite seleccionar rangos de fecha, estado y sede.
- Muestra listado detallado con totales.
RF-075
Contador
Generar reportes de ventas por periodo y sede.
Conciliar la información financiera.
- El reporte incluye fecha, monto total, impuestos, sede y recepcionista.
- Permite filtrar por mes o trimestre.
- El formato es compatible con conciliación contable.
RF-076
Administrador General
Ver los servicios más solicitados.
Identificar los exámenes con mayor demanda.
- El sistema lista los 10 servicios más vendidos por periodo.
- Muestra cantidad, ingresos generados y porcentaje de participación.
- Incluye gráficos para una mejor visualización.
RF-077
Contador
Ver reportes de ventas por método de pago
Verificar la distribución de ingresos por tipo de cobro.
- El sistema muestra resumen por Tarjeta, Transferencia, Yape/Plin.
- Permite exportar y filtrar por sede y fecha.
- Incluye totales y porcentajes.
RF-078
Supervisor de Sede
Ver un reporte de pacientes nuevos y recurrentes
Evaluar la fidelización de clientes.
- El reporte distingue pacientes nuevos (primera visita) y recurrentes (con historial).
- Permite seleccionar rango de fechas.
- Incluye gráfico comparativo.
RF-079
Administrador General
Comparar las ventas mensuales entre periodos.
Evaluar el crecimiento del laboratorio.
- El sistema muestra gráfico de líneas o barras comparando las ventas de los últimos 12 meses.
- Permite exportar el comparativo.
- Se actualiza automáticamente.
RF-080
Supervisor de Sede
Aplicar filtros dinámicos en los reportes.
Obtener información específica de manera rápida.
- Los reportes permiten filtrar por fecha, sede y recepcionista.
- Los filtros se aplican sin recargar la página.
- Se puede limpiar o restablecer los filtros.
RF-081
Administrador General
Exportar los reportes a PDF
Compartirlos con otras áreas o archivarlos.
- Los reportes se exportan con formato legible y logos institucionales.
- La exportación conserva filtros aplicados.
- Compatible con PDF.
RF-082
Administrador General
Visualizar gráficos estadísticos en los reportes.
Analizar las tendencias de manera visual.
- El sistema genera gráficos de barras, líneas o pastel según el tipo de reporte.
- Los gráficos son interactivos.
- Se actualizan al aplicar filtros.
Módulo de Configuración
Requerimiento
Como
Quiero
Para
Criterios de aceptación
RF-083
Administrador General
Gestionar las sedes del laboratorio.
Mantener actualizada la información de contacto y ubicación.
- Permite crear, editar y eliminar sedes.
- Cada sede tiene nombre, dirección, teléfono y código identificador.
- No permite ingresar duplicados.
RF-084
Administrador General
Configurar el porcentaje de IGV
Garantizar el cálculo correcto de los montos facturados.
- El sistema permite definir el porcentaje vigente de IGV.
- Los cambios se reflejan automáticamente en las órdenes.
- Solo el administrador puede modificarlo.
RF-085
Administrador General
Registrar los datos de la empresa (RUC, razón social, logo)
Incluirlos en los comprobantes y reportes.
- Se registran los campos RUC, razón social, dirección y logo.
- La información se muestra en facturas, boletas y reportes oficiales.
- Solo accesible a administradores.
RF-086
Administrador General
Configurar las credenciales SUNAT o PSE.
Habilitar la emisión de comprobantes electrónicos.
- Permite ingresar usuario, clave SOL y credenciales del PSE.
- El sistema valida la conexión con SUNAT.
- Solo el administrador puede modificarlo.
RF-087
Administrador General
Configurar el servidor de correo SMTP.
Enviar notificaciones automáticas y comprobantes por email.
- Permite definir host, puerto, usuario y contraseña SMTP.
- Se puede probar el envío de un correo de prueba.
- El sistema encripta la contraseña.
RF-088
Supervisor de Sede
Ajustar parámetros locales del sistema.
Definir hora de cierre automático y duración de sesiones activas.
- El sistema permite modificar hora de cierre diario y tiempo máximo de sesión.
- Los cambios solo afectan a la sede configurada.
- Se registra el historial de cambios.
RF-089
Administrador General
Tener backups automáticos de la base de datos.
Proteger la información ante fallos.
- El sistema genera copias automáticas diarias en horario programado.
- Permite definir la ruta o almacenamiento en la nube.
- Se notifican errores de respaldo.
RF-090
Administrador General
Restaurar un backup del sistema
Recuperar información en caso de pérdida o error.
- Permite seleccionar un archivo de backup y restaurar.
- Muestra confirmación antes de proceder.
- Solo usuarios con rol de Administrador pueden ejecutar esta acción.


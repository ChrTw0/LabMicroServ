# Manual de Instalación de la Aplicación

Este documento describe los pasos necesarios para instalar y ejecutar la aplicación de laboratorio clínico en un entorno de desarrollo local utilizando Docker.

## 1. Prerrequisitos

Asegúrese de tener instalados los siguientes programas en su sistema:

- **Git:** Para clonar el repositorio del proyecto.
- **Docker:** Para la creación y gestión de contenedores.
- **Docker Compose:** Para orquestar los contenedores de los microservicios.

## 2. Instalación

Siga estos pasos para configurar el proyecto en su máquina local:

### 2.1. Clonar el Repositorio

Abra una terminal o consola de comandos y ejecute el siguiente comando para clonar el repositorio del proyecto:

```bash
git clone <URL_DEL_REPOSITORIO>
```

Reemplace `<URL_DEL_REPOSITORIO>` con la URL real del repositorio Git.

### 2.2. Navegar al Directorio del Proyecto

Una vez clonado el repositorio, acceda al directorio raíz del proyecto:

```bash
cd LabMicroServ
```

## 3. Ejecución de la Aplicación

La aplicación se ejecuta como un conjunto de microservicios orquestados por Docker Compose.

### 3.1. Construir y Levantar los Contenedores

Desde el directorio raíz del proyecto, ejecute el siguiente comando para construir las imágenes de los contenedores y levantarlos en segundo plano:

```bash
docker-compose up -d --build
```

Este comando realizará las siguientes acciones:
- **Construirá las imágenes de Docker** para cada microservicio (`user-service`, `patient-service`, `order-service`, `billing-service`, etc.) y para el `frontend`.
- **Creará y levantará los contenedores** para cada servicio, incluyendo las bases de datos.
- La opción `-d` (detached) ejecuta los contenedores en segundo plano.

Puede verificar el estado de los contenedores con el siguiente comando:

```bash
docker-compose ps
```

### 3.2. Acceder a la Aplicación

Una vez que todos los contenedores estén en funcionamiento, puede acceder a la aplicación web desde su navegador en la siguiente URL:

- **Frontend:** [http://localhost:5173](http://localhost:5173)

## 4. Poblado Inicial de Datos (Seeding)

Para que la aplicación funcione correctamente, es necesario poblar las bases de datos con datos iniciales. Esto incluye la creación de roles, usuarios por defecto y otros catálogos.

Los siguientes comandos deben ejecutarse desde la raíz del proyecto, en una terminal aparte, mientras los contenedores están en ejecución.

### 4.1. Poblar Datos del Servicio de Usuarios

Este comando creará roles por defecto y un usuario administrador.

```bash
docker-compose exec user-service python seed_data.py
```

### 4.2. Poblar Datos del Servicio de Pacientes

Este comando creará pacientes de ejemplo.

```bash
docker-compose exec patient-service python seed_data.py
```

### 4.3. Poblar Datos del Servicio de Órdenes

Este comando creará un catálogo de servicios de ejemplo.

```bash
docker-compose exec order-service python seed_data.py
```

### 4.4. Poblar Datos del Servicio de Facturación

Este comando creará datos iniciales para el servicio de facturación.

```bash
docker-compose exec billing-service python seed_data.py
```

### 4.5. Sincronizar Pacientes con Usuarios

Después de poblar los datos de pacientes y usuarios, ejecute este script para asegurarse de que todos los pacientes con un email tengan una cuenta de usuario correspondiente.

Primero, copie el script al contenedor:
```bash
docker cp scripts/sync_patients_to_users.py labmic_user_service:/app/sync_patients_to_users.py
```

Luego, ejecútelo:
```bash
docker-compose exec -e PYTHONPATH=/app -e PATIENT_DB_URL="postgresql+asyncpg://postgres:1234@patient-db:5432/patient_db" -e USER_DB_URL="postgresql+asyncpg://postgres:1234@user-db:5432/user_db" user-service python /app/sync_patients_to_users.py
```

## 5. Credenciales de Acceso

Después de poblar los datos, puede acceder a la aplicación con las siguientes credenciales de prueba:

- **Email:** `admin@labclinico.com`
- **Contraseña:** `Admin123`

¡La instalación ha finalizado! Ya puede explorar la aplicación.

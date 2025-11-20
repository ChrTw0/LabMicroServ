# 📁 Scripts del Proyecto

Esta carpeta contiene todos los scripts de gestión de Docker.

## 🪟 Scripts Windows (.bat)

- `start.bat` - Inicia todos los servicios
- `stop.bat` - Detiene todos los servicios
- `restart.bat` - Reinicia servicios
- `status.bat` - Estado del sistema
- `logs.bat` - Ver logs
- `build.bat` - Construir imágenes
- `db-only.bat` - Solo bases de datos
- `shell.bat` - Entrar al shell
- `clean.bat` - Limpiar todo (⚠️ borra datos)

## 🐧 Scripts Linux/Mac (.sh)

Los mismos scripts pero para Bash (Git Bash, WSL, Linux, Mac)

## 📄 Documentación

- `COMANDOS.txt` - Guía rápida de comandos
- `SCRIPTS.md` - Documentación detallada

## 🚀 Uso desde la raíz del proyecto

Los scripts principales están disponibles directamente desde la raíz:

```cmd
REM Desde C:\Users\Tekim\Desktop\LabMicroServ\
start.bat
stop.bat
build.bat
status.bat
logs.bat user-service
```

Estos son "wrappers" que llaman a los scripts de esta carpeta.

## 🔧 Otros archivos

- `alembic_env_template.py` - Template para configurar Alembic
- `init-alembic.sh` - Script de inicialización de Alembic
- `generate_services.py` - Script generador de estructura (ya usado)

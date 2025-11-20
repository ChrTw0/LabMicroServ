@echo off
echo ========================================
echo   ADVERTENCIA - LIMPIEZA COMPLETA
echo ========================================
echo.
echo Este script eliminara:
echo   - Todos los contenedores
echo   - Todos los volumenes (DATOS DE LA BASE DE DATOS)
echo   - Todas las imagenes del proyecto
echo.
set /p confirmacion="Estas seguro? (escribe SI para confirmar): "

if not "%confirmacion%"=="SI" (
    echo.
    echo [X] Operacion cancelada
    echo.
    pause
    exit /b
)

echo.
echo [*] Limpiando todo...
echo.

REM Detener y eliminar contenedores y volumenes
docker-compose down -v

REM Eliminar imagenes
echo.
echo [*] Eliminando imagenes...
docker-compose down --rmi all

echo.
echo [OK] Limpieza completada
echo.
echo Para volver a empezar:
echo   1. build.bat
echo   2. start.bat
echo.
pause

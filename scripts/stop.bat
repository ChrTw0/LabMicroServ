@echo off
echo ========================================
echo   Deteniendo Sistema de Laboratorio
echo ========================================
echo.

docker-compose down

echo.
echo [OK] Todos los servicios han sido detenidos
echo.
echo NOTA: Para eliminar tambien los volumenes (BORRA DATOS):
echo       docker-compose down -v
echo.
pause

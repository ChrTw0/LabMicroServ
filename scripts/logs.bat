@echo off
if "%1"=="" (
    echo ========================================
    echo   Logs de TODOS los servicios
    echo ========================================
    echo   (Presiona Ctrl+C para salir)
    echo.
    docker-compose logs -f --tail=100
) else (
    echo ========================================
    echo   Logs de %1
    echo ========================================
    echo   (Presiona Ctrl+C para salir)
    echo.
    docker-compose logs -f --tail=100 %1
)

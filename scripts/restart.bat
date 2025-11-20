@echo off
if "%1"=="" (
    echo ========================================
    echo   Reiniciando TODOS los servicios
    echo ========================================
    echo.
    docker-compose restart
    echo.
    echo [OK] Servicios reiniciados
) else (
    echo ========================================
    echo   Reiniciando %1
    echo ========================================
    echo.
    docker-compose restart %1
    echo.
    echo [OK] %1 reiniciado
    echo.
    echo Ver logs: logs.bat %1
)
echo.
pause

@echo off
if "%1"=="" (
    echo ========================================
    echo   Error: Debes especificar un servicio
    echo ========================================
    echo.
    echo Uso: shell.bat ^<servicio^>
    echo.
    echo Servicios disponibles:
    echo    - user-service
    echo    - patient-service
    echo    - order-service
    echo    - billing-service
    echo    - configuration-service
    echo    - api-gateway
    echo    - user-db
    echo    - patient-db
    echo    - order-db
    echo    - billing-db
    echo    - config-db
    echo.
    pause
    exit /b 1
)

REM Verificar si es una base de datos
echo %1 | findstr "db" > nul
if %errorlevel%==0 (
    REM Es una base de datos, usar psql
    set DB_NAME=%1
    set DB_NAME=!DB_NAME:-db=_db!
    echo ========================================
    echo   Conectando a PostgreSQL: %DB_NAME%
    echo ========================================
    echo   (escribe \q para salir)
    echo.
    docker-compose exec %1 psql -U postgres -d %DB_NAME%
) else (
    REM Es un servicio, abrir bash
    echo ========================================
    echo   Abriendo shell en %1
    echo ========================================
    echo   (escribe 'exit' para salir)
    echo.
    docker-compose exec %1 bash
)

@echo off
echo ========================================
echo   Iniciando solo Bases de Datos
echo ========================================
echo.

docker-compose up -d user-db patient-db order-db billing-db config-db

echo.
echo [*] Esperando que las bases de datos esten listas...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo   Estado de las Bases de Datos
echo ========================================
docker-compose ps | findstr "db"

echo.
echo ========================================
echo   Conexiones Disponibles
echo ========================================
echo    user_db:       localhost:5432 (postgres/1234)
echo    patient_db:    localhost:5433 (postgres/1234)
echo    order_db:      localhost:5434 (postgres/1234)
echo    billing_db:    localhost:5435 (postgres/1234)
echo    config_db:     localhost:5436 (postgres/1234)
echo.
echo Para conectarte a una BD:
echo    docker-compose exec user-db psql -U postgres -d user_db
echo.
pause

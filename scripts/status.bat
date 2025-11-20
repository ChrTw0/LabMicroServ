@echo off
echo ========================================
echo   Estado de los Servicios
echo ========================================
echo.

docker-compose ps

echo.
echo ========================================
echo   Puertos Ocupados
echo ========================================
echo    5432  - user-db
echo    5433  - patient-db
echo    5434  - order-db
echo    5435  - billing-db
echo    5436  - config-db
echo    8000  - api-gateway
echo    8001  - user-service
echo    8002  - patient-service
echo    8003  - order-service
echo    8004  - billing-service
echo    8005  - configuration-service
echo.
pause

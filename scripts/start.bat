@echo off
echo ========================================
echo   Iniciando Sistema de Laboratorio
echo ========================================
echo.

echo [*] Levantando servicios...
docker-compose up -d

echo.
echo [*] Esperando que los servicios esten listos...
timeout /t 10 /nobreak > nul

echo.
echo ========================================
echo   Estado de los Servicios
echo ========================================
docker-compose ps

echo.
echo ========================================
echo   Health Checks
echo ========================================
echo    User Service:          http://localhost:8001/health
echo    Patient Service:       http://localhost:8002/health
echo    Order Service:         http://localhost:8003/health
echo    Billing Service:       http://localhost:8004/health
echo    Configuration Service: http://localhost:8005/health
echo    API Gateway:           http://localhost:8000/health

echo.
echo ========================================
echo   Documentacion Swagger
echo ========================================
echo    User Service:          http://localhost:8001/docs
echo    Patient Service:       http://localhost:8002/docs
echo    Order Service:         http://localhost:8003/docs
echo    Billing Service:       http://localhost:8004/docs
echo    Configuration Service: http://localhost:8005/docs
echo    API Gateway:           http://localhost:8000/docs

echo.
echo ========================================
echo   Comandos Utiles
echo ========================================
echo    Ver logs:      logs.bat
echo    Detener:       stop.bat
echo    Reiniciar:     restart.bat
echo    Estado:        status.bat
echo.
pause

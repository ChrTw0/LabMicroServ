@echo off
if "%1"=="" (
    echo ========================================
    echo   Construyendo TODAS las imagenes
    echo ========================================
    echo   (Esto puede tomar varios minutos)
    echo.
    docker-compose build
    echo.
    echo [OK] Todas las imagenes construidas
) else (
    echo ========================================
    echo   Construyendo imagen de %1
    echo ========================================
    echo.
    docker-compose build %1
    echo.
    echo [OK] Imagen de %1 construida
)
echo.
echo Para iniciar los servicios: start.bat
echo.
pause

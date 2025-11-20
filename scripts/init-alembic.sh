#!/bin/bash

# Script para inicializar Alembic en todos los servicios
# Uso: ./scripts/init-alembic.sh

echo "🔧 Inicializando Alembic en todos los servicios..."
echo ""

# Lista de servicios
SERVICES=(
    "user-service"
    "patient-service"
    "order-service"
    "billing-service"
    "configuration-service"
    "reporting-service"
)

for SERVICE in "${SERVICES[@]}"; do
    echo "📦 Procesando $SERVICE..."

    cd "$SERVICE" || exit

    # Verificar si alembic ya está inicializado
    if [ -d "alembic" ]; then
        echo "   ⚠️  Alembic ya está inicializado en $SERVICE, saltando..."
    else
        echo "   ✅ Inicializando Alembic..."
        alembic init alembic

        # Actualizar alembic.ini con configuración correcta
        echo "   🔧 Configurando alembic.ini..."

        # Comentar la línea de sqlalchemy.url en alembic.ini
        sed -i 's/^sqlalchemy.url =/#sqlalchemy.url =/' alembic/alembic.ini

        echo "   ✅ Alembic configurado correctamente"
    fi

    cd ..
    echo ""
done

echo "✨ Proceso completado!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Actualizar cada alembic/env.py para usar tu config"
echo "   2. Crear migración inicial: alembic revision --autogenerate -m 'Initial migration'"
echo "   3. Aplicar migración: alembic upgrade head"

#!/bin/bash

# Script para entrar al shell de un servicio
# Uso: ./shell.sh <servicio>
# Ejemplo: ./shell.sh user-service

if [ -z "$1" ]; then
    echo "❌ Error: Debes especificar un servicio"
    echo ""
    echo "Uso: ./shell.sh <servicio>"
    echo ""
    echo "Servicios disponibles:"
    echo "   - user-service"
    echo "   - patient-service"
    echo "   - order-service"
    echo "   - billing-service"
    echo "   - configuration-service"
    echo "   - user-db"
    echo "   - patient-db"
    echo "   - order-db"
    echo "   - billing-db"
    echo "   - config-db"
    exit 1
fi

# Si es una base de datos, usar psql
if [[ "$1" == *"-db" ]]; then
    DB_NAME="${1%-db}_db"
    echo "🐘 Conectando a PostgreSQL: $DB_NAME"
    echo "   (escribe \q para salir)"
    echo ""
    docker-compose exec $1 psql -U postgres -d $DB_NAME
else
    echo "💻 Abriendo shell en $1..."
    echo "   (escribe 'exit' para salir)"
    echo ""
    docker-compose exec $1 bash
fi

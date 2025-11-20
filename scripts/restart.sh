#!/bin/bash

# Script para reiniciar servicios
# Uso: ./restart.sh [servicio]
# Ejemplo: ./restart.sh user-service

if [ -z "$1" ]; then
    echo "🔄 Reiniciando TODOS los servicios..."
    echo ""
    docker-compose restart
    echo ""
    echo "✅ Servicios reiniciados"
else
    echo "🔄 Reiniciando $1..."
    echo ""
    docker-compose restart $1
    echo ""
    echo "✅ $1 reiniciado"
fi

echo ""
echo "💡 Ver logs: ./logs.sh $1"

#!/bin/bash

# Script para ver logs
# Uso: ./logs.sh [servicio]
# Ejemplo: ./logs.sh user-service

if [ -z "$1" ]; then
    echo "📋 Mostrando logs de TODOS los servicios..."
    echo "   (Presiona Ctrl+C para salir)"
    echo ""
    docker-compose logs -f --tail=100
else
    echo "📋 Mostrando logs de $1..."
    echo "   (Presiona Ctrl+C para salir)"
    echo ""
    docker-compose logs -f --tail=100 $1
fi

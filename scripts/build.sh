#!/bin/bash

# Script para construir las imágenes Docker
# Uso: ./build.sh [servicio]
# Ejemplo: ./build.sh user-service

if [ -z "$1" ]; then
    echo "🔨 Construyendo TODAS las imágenes Docker..."
    echo "   (Esto puede tomar varios minutos)"
    echo ""
    docker-compose build
    echo ""
    echo "✅ Todas las imágenes construidas"
else
    echo "🔨 Construyendo imagen de $1..."
    echo ""
    docker-compose build $1
    echo ""
    echo "✅ Imagen de $1 construida"
fi

echo ""
echo "💡 Para iniciar los servicios: ./start.sh"

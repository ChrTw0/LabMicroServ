#!/bin/bash

# Script para limpiar todo (contenedores, volúmenes, imágenes)
# Uso: ./clean.sh

echo "⚠️  ADVERTENCIA: Este script eliminará:"
echo "   - Todos los contenedores"
echo "   - Todos los volúmenes (DATOS DE LA BASE DE DATOS)"
echo "   - Todas las imágenes del proyecto"
echo ""
read -p "¿Estás seguro? (escribe 'SI' para confirmar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🧹 Limpiando todo..."
echo ""

# Detener y eliminar contenedores y volúmenes
docker-compose down -v

# Eliminar imágenes
echo ""
echo "🗑️  Eliminando imágenes..."
docker-compose down --rmi all

echo ""
echo "✅ Limpieza completada"
echo ""
echo "💡 Para volver a empezar:"
echo "   1. ./build.sh"
echo "   2. ./start.sh"

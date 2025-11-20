#!/bin/bash

# Script para detener todos los servicios
# Uso: ./stop.sh

echo "🛑 Deteniendo Sistema de Laboratorio Clínico..."
echo ""

docker-compose down

echo ""
echo "✅ Todos los servicios han sido detenidos"
echo ""
echo "💡 Para eliminar también los volúmenes (BORRA DATOS):"
echo "   docker-compose down -v"

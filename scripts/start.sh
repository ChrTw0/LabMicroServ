#!/bin/bash

# Script para iniciar todos los servicios
# Uso: ./start.sh

echo "🚀 Iniciando Sistema de Laboratorio Clínico..."
echo ""

# Levantar todos los servicios
docker-compose up -d

echo ""
echo "⏳ Esperando que los servicios estén listos..."
sleep 10

echo ""
echo "✅ Estado de los servicios:"
docker-compose ps

echo ""
echo "📊 Health Checks:"
echo "   User Service:          http://localhost:8001/health"
echo "   Patient Service:       http://localhost:8002/health"
echo "   Order Service:         http://localhost:8003/health"
echo "   Billing Service:       http://localhost:8004/health"
echo "   Configuration Service: http://localhost:8005/health"

echo ""
echo "📚 Documentación Swagger:"
echo "   User Service:          http://localhost:8001/docs"
echo "   Patient Service:       http://localhost:8002/docs"
echo "   Order Service:         http://localhost:8003/docs"
echo "   Billing Service:       http://localhost:8004/docs"
echo "   Configuration Service: http://localhost:8005/docs"

echo ""
echo "💡 Comandos útiles:"
echo "   Ver logs:      ./logs.sh"
echo "   Detener:       ./stop.sh"
echo "   Reiniciar:     ./restart.sh"
echo "   Estado:        ./status.sh"

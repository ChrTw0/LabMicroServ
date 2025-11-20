#!/bin/bash

# Script para levantar SOLO las bases de datos
# Útil para desarrollo local sin Docker en los servicios
# Uso: ./db-only.sh

echo "💾 Iniciando solo las bases de datos..."
echo ""

docker-compose up -d user-db patient-db order-db billing-db config-db

echo ""
echo "⏳ Esperando que las bases de datos estén listas..."
sleep 5

echo ""
echo "✅ Estado de las bases de datos:"
docker-compose ps | grep -E "user-db|patient-db|order-db|billing-db|config-db"

echo ""
echo "📊 Conexiones disponibles:"
echo "   user_db:          localhost:5432 (postgres/1234)"
echo "   patient_db:       localhost:5433 (postgres/1234)"
echo "   order_db:         localhost:5434 (postgres/1234)"
echo "   billing_db:       localhost:5435 (postgres/1234)"
echo "   config_db:        localhost:5436 (postgres/1234)"

echo ""
echo "💡 Para conectarte a una BD:"
echo "   docker-compose exec user-db psql -U postgres -d user_db"

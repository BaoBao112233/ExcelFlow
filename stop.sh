#!/bin/bash
# Stop ExcelFlow Docker services

echo "🛑 Stopping ExcelFlow services..."

if docker compose version &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo "✅ Services stopped"
echo ""
echo "To remove volumes and data:"
echo "  docker-compose down -v"
echo ""
echo "To remove images:"
echo "  docker-compose down --rmi all"

#!/bin/bash

echo "🚀 Starting R1L Requirement Management System..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Build and start services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services..."
sleep 15

echo ""
echo "✅ System ready!"
echo ""
echo "📍 Access:"
echo "   Frontend:  http://localhost:3001"
echo "   Backend:   http://localhost:8001/docs"
echo "   Database:  localhost:5434"
echo ""
echo "💡 Commands:"
echo "   Logs:      docker-compose logs -f"
echo "   Stop:      docker-compose down"
echo "   Restart:   docker-compose restart"
echo ""

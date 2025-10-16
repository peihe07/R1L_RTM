#!/bin/bash

echo " Starting Requirement Management System..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo " Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start all services
echo "Building and starting services..."
docker-compose up --build -d

echo ""
echo "Waiting for services to start...ㄨ"
sleep 15

# Check service status
echo ""
echo " Service Status:"
docker-compose ps

echo ""
echo " System should be ready."
echo ""
echo " Access your application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Database: localhost:5432"
echo ""

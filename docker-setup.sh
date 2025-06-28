#!/bin/bash

# Docker Setup Script for Flask Bug Tracker
# This script builds and runs the application using Docker Compose

echo "🐳 Flask Bug Tracker - Docker Setup"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Docker Compose is available"

# Stop any existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo ""
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps

# Check MongoDB connection
echo ""
echo "🔍 Testing MongoDB connection..."
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" --quiet

# Check Flask application health
echo ""
echo "🔍 Testing Flask application..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Flask application is healthy"
else
    echo "❌ Flask application health check failed"
fi

# Show logs
echo ""
echo "📋 Recent logs:"
echo "==============="
docker-compose logs --tail=10

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Application URLs:"
echo "  - Flask App: http://localhost:5000"
echo "  - Health Check: http://localhost:5000/health"
echo "  - MongoDB: localhost:27017"
echo "  - Redis: localhost:6379"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Access MongoDB shell: docker-compose exec mongodb mongosh"
echo ""

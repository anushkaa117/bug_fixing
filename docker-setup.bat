@echo off
REM Docker Setup Script for Flask Bug Tracker (Windows)
REM This script builds and runs the application using Docker Compose

echo 🐳 Flask Bug Tracker - Docker Setup
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo ✅ Docker Compose is available

REM Stop any existing containers
echo.
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start services
echo.
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo 📊 Service Status:
echo ==================
docker-compose ps

REM Check MongoDB connection
echo.
echo 🔍 Testing MongoDB connection...
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" --quiet

REM Check Flask application health
echo.
echo 🔍 Testing Flask application...
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Flask application is healthy
) else (
    echo ❌ Flask application health check failed
)

REM Show logs
echo.
echo 📋 Recent logs:
echo ===============
docker-compose logs --tail=10

echo.
echo 🎉 Setup complete!
echo.
echo 📱 Application URLs:
echo   - Flask App: http://localhost:5000
echo   - Health Check: http://localhost:5000/health
echo   - MongoDB: localhost:27017
echo   - Redis: localhost:6379
echo.
echo 🔧 Useful commands:
echo   - View logs: docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Restart services: docker-compose restart
echo   - Access MongoDB shell: docker-compose exec mongodb mongosh
echo.
pause

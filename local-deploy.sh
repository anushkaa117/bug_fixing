#!/bin/bash

# Bug Tracker Local Deployment Script
# This script sets up and runs the Flask Bug Tracker application locally

set -e  # Exit on any error

echo "🐛 Bug Tracker Local Deployment"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif docker-compose --version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p instance
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p logs
    
    print_success "Directories created"
}

# Set up environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///instance/bugtracker.db

# Mail Configuration (optional for development)
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=
MAIL_PASSWORD=

# Application Settings
ADMIN_EMAIL=admin@bugtracker.local
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
EOF
        print_success ".env file created"
    else
        print_warning ".env file already exists"
    fi
}

# Build and start the application
start_application() {
    print_status "Building and starting the application..."
    
    # Use development compose file for simpler setup
    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down --remove-orphans
    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml build --no-cache
    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml up -d
    
    print_success "Application started successfully"
}

# Wait for application to be ready
wait_for_app() {
    print_status "Waiting for application to be ready..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/ &> /dev/null; then
            print_success "Application is ready!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Application failed to start within expected time"
            print_status "Checking logs..."
            $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml logs web
            exit 1
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
}

# Show application info
show_info() {
    echo ""
    echo "🎉 Bug Tracker is now running!"
    echo "================================"
    echo "🌐 Application URL: http://localhost:5000"
    echo "👤 Default Admin Login:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "📋 Available Commands:"
    echo "   View logs:    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml logs -f"
    echo "   Stop app:     $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down"
    echo "   Restart app:  $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml restart"
    echo "   Shell access: $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml exec web bash"
    echo ""
    echo "🔧 Development Notes:"
    echo "   - Code changes will auto-reload"
    echo "   - Database file: ./instance/bugtracker.db"
    echo "   - Static files: ./static/"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down --remove-orphans
}

# Handle script interruption
trap cleanup EXIT

# Main execution
main() {
    echo "Starting Bug Tracker local deployment..."
    echo ""
    
    check_docker
    check_docker_compose
    create_directories
    setup_environment
    start_application
    wait_for_app
    show_info
    
    # Keep script running to show logs
    print_status "Showing application logs (Ctrl+C to stop)..."
    $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml logs -f
}

# Parse command line arguments
case "${1:-}" in
    "stop")
        print_status "Stopping Bug Tracker..."
        $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down
        print_success "Bug Tracker stopped"
        ;;
    "restart")
        print_status "Restarting Bug Tracker..."
        $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml restart
        print_success "Bug Tracker restarted"
        ;;
    "logs")
        print_status "Showing Bug Tracker logs..."
        $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml logs -f
        ;;
    "shell")
        print_status "Opening shell in Bug Tracker container..."
        $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml exec web bash
        ;;
    "clean")
        print_status "Cleaning up Bug Tracker..."
        $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down --volumes --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    "help"|"-h"|"--help")
        echo "Bug Tracker Local Deployment Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Start the application"
        echo "  stop       Stop the application"
        echo "  restart    Restart the application"
        echo "  logs       Show application logs"
        echo "  shell      Open shell in container"
        echo "  clean      Clean up containers and volumes"
        echo "  help       Show this help message"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

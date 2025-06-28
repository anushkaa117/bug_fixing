#!/bin/bash

# Bug Tracker Vercel Deployment Script
# This script deploys the Flask Bug Tracker with React frontend to Vercel

set -e  # Exit on any error

echo "🚀 Bug Tracker Vercel Deployment"
echo "================================="

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

# Check if Vercel CLI is installed
check_vercel_cli() {
    print_status "Checking Vercel CLI installation..."
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
        print_success "Vercel CLI installed successfully"
    else
        print_success "Vercel CLI is already installed"
    fi
}

# Check if user is logged in to Vercel
check_vercel_auth() {
    print_status "Checking Vercel authentication..."
    
    if ! vercel whoami &> /dev/null; then
        print_warning "Not logged in to Vercel. Please login..."
        vercel login
    else
        print_success "Already logged in to Vercel"
    fi
}

# Build frontend locally to check for errors
build_frontend() {
    print_status "Building frontend locally to check for errors..."
    
    cd frontend
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    print_status "Building frontend..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Frontend build successful"
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    cd ..
}

# Deploy to Vercel
deploy_to_vercel() {
    print_status "Deploying to Vercel..."
    
    # Deploy with production flag
    vercel --prod
    
    if [ $? -eq 0 ]; then
        print_success "Deployment successful!"
        print_status "Your app should be available at the URL shown above"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Set environment variables reminder
show_env_reminder() {
    print_warning "IMPORTANT: Make sure you have set the following environment variables in Vercel:"
    echo "  - MONGO_USERNAME"
    echo "  - MONGO_PASSWORD" 
    echo "  - MONGO_CLUSTER"
    echo "  - MONGO_DATABASE"
    echo "  - SECRET_KEY"
    echo ""
    echo "You can set these at: https://vercel.com/dashboard -> Your Project -> Settings -> Environment Variables"
    echo ""
}

# Main deployment process
main() {
    print_status "Starting deployment process..."
    
    show_env_reminder
    
    check_vercel_cli
    check_vercel_auth
    build_frontend
    deploy_to_vercel
    
    print_success "Deployment process completed!"
}

# Run main function
main

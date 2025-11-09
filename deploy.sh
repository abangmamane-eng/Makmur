#!/bin/bash

# =============================================================================
# Toko Kopi Makmur - Deployment Script
# =============================================================================
# This script helps deploy the application to various platforms
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
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

# Check if environment file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual configuration before running the application."
        else
            print_error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    python3 -m pip install --user -r requirements.txt
    print_success "Dependencies installed successfully"
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    if [ -f init_db.py ]; then
        python3 init_db.py
        print_success "Database initialized successfully"
    else
        print_warning "init_db.py not found. Database initialization skipped."
    fi
}

# Build Docker image
build_docker() {
    print_info "Building Docker image..."
    docker build -t kopi-makmur:latest .
    print_success "Docker image built successfully"
}

# Run with Docker Compose
run_docker_compose() {
    print_info "Starting application with Docker Compose..."
    docker-compose up -d
    print_success "Application started with Docker Compose"
}

# Deploy to Netlify
deploy_netlify() {
    print_info "Deploying to Netlify..."
    
    if ! command -v netlify &> /dev/null; then
        print_info "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi
    
    if [ -z "$NETLIFY_AUTH_TOKEN" ]; then
        print_error "NETLIFY_AUTH_TOKEN environment variable not set"
        exit 1
    fi
    
    if [ -z "$NETLIFY_SITE_ID" ]; then
        print_error "NETLIFY_SITE_ID environment variable not set"
        exit 1
    fi
    
    netlify deploy --prod
    print_success "Deployed to Netlify successfully"
}

# Deploy to Heroku
deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Please install it first."
        exit 1
    fi
    
    if [ -z "$HEROKU_API_KEY" ]; then
        print_error "HEROKU_API_KEY environment variable not set"
        exit 1
    fi
    
    if [ -z "$HEROKU_APP_NAME" ]; then
        print_error "HEROKU_APP_NAME environment variable not set"
        exit 1
    fi
    
    heroku container:push web -a $HEROKU_APP_NAME
    heroku container:release web -a $HEROKU_APP_NAME
    print_success "Deployed to Heroku successfully"
}

# Deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_info "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    if [ -z "$RAILWAY_TOKEN" ]; then
        print_error "RAILWAY_TOKEN environment variable not set"
        exit 1
    fi
    
    railway deploy
    print_success "Deployed to Railway successfully"
}

# Main menu
show_menu() {
    echo ""
    echo "======================================"
    echo "  Toko Kopi Makmur - Deployment Tool  "
    echo "======================================"
    echo ""
    echo "1. Setup local development environment"
    echo "2. Run with Docker Compose"
    echo "3. Build Docker image only"
    echo "4. Deploy to Netlify"
    echo "5. Deploy to Heroku"
    echo "6. Deploy to Railway"
    echo "7. Run health check"
    echo "8. View logs"
    echo "9. Stop all services"
    echo "0. Exit"
    echo ""
}

# Health check
health_check() {
    print_info "Running health check..."
    
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Application is healthy and running on http://localhost:5000"
    else
        print_error "Application is not responding. Please check the logs."
    fi
}

# View logs
view_logs() {
    print_info "Showing application logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Stop services
stop_services() {
    print_info "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

# Main script
main() {
    case $1 in
        "setup")
            check_env_file
            install_dependencies
            init_database
            print_success "Setup completed! Run: python3 app.py"
            ;;
        "docker")
            check_env_file
            build_docker
            run_docker_compose
            health_check
            ;;
        "netlify")
            deploy_netlify
            ;;
        "heroku")
            deploy_heroku
            ;;
        "railway")
            deploy_railway
            ;;
        "health")
            health_check
            ;;
        "logs")
            view_logs
            ;;
        "stop")
            stop_services
            ;;
        "menu"|"")
            while true; do
                show_menu
                read -p "Choose an option: " choice
                case $choice in
                    1) 
                        check_env_file
                        install_dependencies
                        init_database
                        print_success "Setup completed! Run: python3 app.py"
                        ;;
                    2) 
                        check_env_file
                        build_docker
                        run_docker_compose
                        health_check
                        ;;
                    3) 
                        build_docker
                        ;;
                    4) 
                        deploy_netlify
                        ;;
                    5) 
                        deploy_heroku
                        ;;
                    6) 
                        deploy_railway
                        ;;
                    7) 
                        health_check
                        ;;
                    8) 
                        view_logs
                        ;;
                    9) 
                        stop_services
                        ;;
                    0) 
                        print_success "Goodbye!"
                        exit 0
                        ;;
                    *) 
                        print_error "Invalid option. Please try again."
                        ;;
                esac
                echo ""
                read -p "Press Enter to continue..."
            done
            ;;
        *)
            print_error "Usage: $0 [setup|docker|netlify|heroku|railway|health|logs|stop|menu]"
            echo "Use '$0 menu' for interactive mode"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
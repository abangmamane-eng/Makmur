# Toko Kopi Makmur - Makefile
# Simplified development and deployment commands

.PHONY: help setup install dev run build docker docker-build docker-run test lint clean deploy-static

# Default target
help: ## Show this help message
	@echo "Toko Kopi Makmur - Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	@cp .env.example .env
	@echo "✅ Environment file created. Please edit .env with your configuration"
	@make install
	@make init-db

install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

dev: ## Start development server
	@echo "🏃 Starting development server..."
	@make init-db
	python app.py

init-db: ## Initialize database with sample data
	@echo "🗄️ Initializing database..."
	@if [ -f init_db.py ]; then \
		python init_db.py; \
		echo "✅ Database initialized"; \
	else \
		echo "⚠️ init_db.py not found"; \
	fi

build: ## Build static version for Netlify
	@echo "🏗️ Building static version..."
	@if [ -f static_build.py ]; then \
		python static_build.py; \
		echo "✅ Static build completed. Check 'dist' directory"; \
	else \
		echo "❌ static_build.py not found"; \
	fi

docker: ## Start with Docker Compose
	@echo "🐳 Starting with Docker Compose..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose up -d; \
		echo "✅ Services started. Visit http://localhost:5000"; \
		echo "📊 Health check: http://localhost:5000/health"; \
	else \
		echo "❌ docker-compose.yml not found"; \
	fi

docker-build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	@if [ -f Dockerfile ]; then \
		docker build -t kopi-makmur:latest .; \
		echo "✅ Docker image built: kopi-makmur:latest"; \
	else \
		echo "❌ Dockerfile not found"; \
	fi

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	@make docker-build
	docker run -d --name kopi-makmur -p 5000:5000 kopi-makmur:latest
	@echo "✅ Container running. Visit http://localhost:5000"

test: ## Run tests
	@echo "🧪 Running tests..."
	@if [ -f test_dinamis.py ]; then \
		python test_dinamis.py; \
	else \
		echo "⚠️ test_dinamis.py not found"; \
	fi

lint: ## Run code linting
	@echo "🔍 Running code analysis..."
	@python -m py_compile app.py
	@echo "✅ Code compiled successfully"

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@rm -rf __pycache__/
	@rm -rf *.pyc
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

deploy: ## Deploy to production (requires environment setup)
	@echo "🚀 Deploying to production..."
	@chmod +x deploy.sh
	@./deploy.sh

deploy-static: ## Build and deploy static version
	@echo "🌐 Building and deploying static version..."
	@make build
	@if [ -d dist ]; then \
		echo "✅ Static version built in 'dist' directory"; \
		echo "📁 Upload contents of 'dist' to Netlify"; \
	else \
		echo "❌ Build failed"; \
	fi

status: ## Show application status
	@echo "📊 Application Status"
	@echo "===================="
	@if [ -f kopi_makmur.db ]; then \
		echo "✅ Database: kopi_makmur.db exists"; \
		echo "📊 Database size: $(shell du -h kopi_makmur.db)"; \
	else \
		echo "❌ Database: kopi_makmur.db not found"; \
	fi
	@if [ -f .env ]; then \
		echo "✅ Environment: .env file exists"; \
	else \
		echo "⚠️ Environment: .env file not found (run 'make setup')"; \
	fi
	@echo "🐳 Docker services:"
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose ps 2>/dev/null || echo "  No Docker Compose services running"; \
	else \
		echo "  Docker Compose not installed"; \
	fi

logs: ## Show application logs
	@if [ -f docker-compose.yml ]; then \
		docker-compose logs -f; \
	else \
		echo "❌ No docker-compose.yml found"; \
	fi

stop: ## Stop all services
	@echo "⏹️ Stopping services..."
	@docker-compose down 2>/dev/null || echo "  No Docker Compose services to stop"
	@docker stop kopi-makmur 2>/dev/null || echo "  No Docker container to stop"
	@echo "✅ Services stopped"

restart: ## Restart services
	@make stop
	@make docker

# Development shortcuts
quick-start: setup dev ## Complete setup and start development server
quick-docker: setup docker ## Complete setup and start with Docker
check-health: ## Check application health
	@curl -f http://localhost:5000/health >/dev/null 2>&1 && echo "✅ Application is healthy" || echo "❌ Application is not responding"
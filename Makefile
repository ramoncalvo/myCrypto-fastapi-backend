# MyCrypto FastAPI Backend - Makefile

.PHONY: help build up down logs clean test dev prod restart

# Default target
help:
	@echo "MyCrypto FastAPI Backend Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment with hot reload"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make dev-logs     - Show development logs"
	@echo "  make dev-down     - Stop development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production environment"
	@echo "  make prod-logs    - Show production logs"
	@echo "  make prod-down    - Stop production environment"
	@echo ""
	@echo "Database:"
	@echo "  make mongo        - Start only MongoDB"
	@echo "  make mongo-ui     - Open MongoDB Express UI"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean Docker containers and volumes"
	@echo "  make restart      - Restart all services"
	@echo "  make test         - Run API tests"
	@echo "  make install      - Install Python dependencies locally"

# Development commands
dev:
	docker-compose -f docker-compose.dev.yml up -d

dev-build:
	docker-compose -f docker-compose.dev.yml up --build -d

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

dev-down:
	docker-compose -f docker-compose.dev.yml down

# Production commands
prod:
	docker-compose up -d

prod-build:
	docker-compose up --build -d

prod-logs:
	docker-compose logs -f

prod-down:
	docker-compose down

# Database commands
mongo:
	docker-compose -f docker-compose.dev.yml up mongodb -d

mongo-ui:
	@echo "Opening MongoDB Express at http://localhost:8081"
	@echo "Username: admin"
	@echo "Password: admin123"
	open http://localhost:8081

# Utility commands
clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	docker system prune -f

restart: down up

test:
	@echo "API available at: http://localhost:8000"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Health Check: http://localhost:8000/health"
	@echo ""
	@echo "Use the .http files in tests/ directory for API testing"

install:
	pip install -r requirements.txt

# Aliases
up: dev
down: dev-down
build: dev-build
logs: dev-logs

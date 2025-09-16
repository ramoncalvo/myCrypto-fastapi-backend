# MyCrypto FastAPI Backend - Makefile

.PHONY: help build up down logs clean test dev prod restart

# Default target
help:
	@echo "MyCrypto FastAPI Backend Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment with hot reload (Clean Architecture)"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make dev-logs     - Show development logs"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-local    - Run Clean Architecture API locally (no Docker)"
	@echo "  make dev-local-mongo - Start only MongoDB + UI for local development"
	@echo ""
	@echo "Testing:"
	@echo "  make test-endpoints    - Run all automated endpoint tests"
	@echo "  make test-auth         - Run authentication tests only"
	@echo "  make test-crypto       - Run crypto asset tests only"
	@echo "  make test-portfolio    - Run portfolio tests only"
	@echo "  make test-transaction  - Run transaction tests only"
	@echo "  make test-endpoint TEST=<name> - Run specific test (auth_register, crypto_list, etc.)"
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
	@echo "  make clean-db     - Reset database (remove volume only)"
	@echo "  make restart      - Restart all services"
	@echo "  make test         - Run API tests"
	@echo "  make install      - Install Python dependencies locally"

# Development commands
dev:
	docker compose -f docker-compose.dev.yml up -d

dev-build:
	docker compose -f docker-compose.dev.yml up --build -d

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

dev-down:
	docker compose -f docker-compose.dev.yml down

# Local development (without Docker)
dev-local:
	@echo "Starting MyCrypto API with Clean Architecture locally..."
	@echo "Make sure MongoDB is running (use 'make mongo' or local MongoDB)"
	uvicorn main_clean:app --host 0.0.0.0 --port 8000 --reload

dev-local-mongo:
	@echo "Starting MongoDB only..."
	docker compose -f docker-compose.dev.yml up mongodb mongo-express -d
	@echo "MongoDB running at: mongodb://localhost:27017"
	@echo "MongoDB Express UI: http://localhost:8081 (admin/admin123)"

# Production commands
prod:
	docker compose up -d

prod-build:
	docker compose up --build -d

prod-logs:
	docker compose logs -f

prod-down:
	docker compose down

# Database commands
mongo:
	docker compose -f docker-compose.dev.yml up mongodb -d

mongo-ui:
	@echo "Opening MongoDB Express at http://localhost:8081"
	@echo "Username: admin"
	@echo "Password: admin123"
	open http://localhost:8081

# Utility commands
clean:
	docker compose -f docker-compose.dev.yml down -v
	docker compose down -v
	docker system prune -f

clean-db:
	docker compose -f docker-compose.dev.yml down
	docker volume rm pybackend_mongodb_data_dev || true
	@echo "Database volume removed. Run 'make dev' to restart with fresh database."

restart: down up

test:
	@echo "API available at: http://localhost:8000"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Health Check: http://localhost:8000/health"
	@echo ""
	@echo "Use the .http files in tests/ directory for API testing"

install:
	pip install -r requirements.txt

# Automated endpoint testing
test-endpoints:
	@echo "Running automated endpoint tests..."
	./run_tests.sh

test-endpoint:
	@echo "🎯 Running specific test: $(TEST)"
	@cd tests && python run_endpoint_tests.py $(TEST)

# Bitso API Integration Tests
test-bitso-public:
	@echo "🌐 Testing Bitso public endpoints..."
	@make test-endpoint TEST=bitso_books
	@make test-endpoint TEST=bitso_ticker
	@make test-endpoint TEST=bitso_overview

test-bitso-private:
	@echo "🔐 Testing Bitso private endpoints..."
	@make test-endpoint TEST=bitso_private

test-bitso-all:
	@echo "🚀 Testing all Bitso endpoints..."
	@make test-bitso-public
	@make test-bitso-private

test-auth:
	@echo "Running authentication tests..."
	./run_tests.sh auth_register
	./run_tests.sh auth_login

test-crypto:
	@echo "Running crypto asset tests..."
	./run_tests.sh crypto_list
	./run_tests.sh crypto_create

test-portfolio:
	@echo "Running portfolio tests..."
	./run_tests.sh portfolio_list
	./run_tests.sh portfolio_create

test-transaction:
	@echo "Running transaction tests..."
	./run_tests.sh transaction_list
	./run_tests.sh transaction_buy
	./run_tests.sh transaction_stats

# Aliases
up: dev
down: dev-down
build: dev-build
logs: dev-logs

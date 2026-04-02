.PHONY: help install dev build prod lint test clean docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Development
install: ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: ## Run development servers
	cd frontend && npm run dev

dev-backend: ## Run backend development server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

dev-frontend: ## Run frontend development server
	cd frontend && npm run dev

build: ## Build frontend
	cd frontend && npm run build

build-backend: ## Build backend
	cd backend && python -m py_compile app/main.py

# Docker
docker-up: ## Start all services
	docker-compose up -d

docker-up-prod: ## Start production services
	docker-compose -f docker-compose.prod.yaml up -d

docker-down: ## Stop all services
	docker-compose down

docker-down-prod: ## Stop production services
	docker-compose -f docker-compose.prod.yaml down

docker-logs: ## View logs
	docker-compose logs -f

docker-ps: ## Show running containers
	docker-compose ps

# Testing
test: ## Run frontend tests
	cd frontend && npm run test

test-backend: ## Run backend tests
	cd backend && python -m pytest

test-e2e: ## Run e2e tests
	cd frontend && npm run test:e2e

test-integration: ## Run integration tests
	cd backend && python -m pytest tests/integration/

# Linting
lint: ## Run linters
	cd frontend && npm run lint

lint-fix: ## Run linters with fix
	cd frontend && npm run format

# Database
db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-reset: ## Reset database (WARNING: destroys data)
	docker-compose down -v
	docker-compose up -d db

db-seed: ## Seed database with test data
	cd backend && python -m scripts.seed

# Utilities
clean: ## Clean up build artifacts
	cd frontend && npm run clean || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

sh: ## Shell into backend container
	docker-compose exec backend sh

psql: ## Connect to PostgreSQL
	docker-compose exec db psql -U luigi -d luigi_chat

redis-cli: ## Connect to Redis
	docker-compose exec redis redis-cli

# Git
commit: ## Commit changes
	git add -A && git commit -m "$$(date +'%Y-%m-%d %H:%M') updates"

push: ## Push to remote
	git push origin main

# Health checks
health: ## Check service health
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8080"
	@echo "API Docs: http://localhost:8080/docs"
	@curl -s http://localhost:8080/api/health || echo "Backend not responding"

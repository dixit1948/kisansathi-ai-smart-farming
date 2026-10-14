.PHONY: dev docker-up docker-down test lint seed ingest clean help

BACKEND_DIR = backend
FRONTEND_DIR = frontend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start backend + frontend with hot reload
	@echo "Starting KisanSathi in dev mode..."
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@cd $(FRONTEND_DIR) && npm run dev

docker-up: ## Start all services via Docker Compose
	docker compose -f docker-compose.yml up --build -d
	@echo "Services started. API: http://localhost:8000  Web: http://localhost:3000"
	@echo "Running seed..."
	@sleep 10
	docker compose exec api python scripts/seed.py

docker-down: ## Stop all Docker services
	docker compose -f docker-compose.yml down

docker-logs: ## Tail Docker logs
	docker compose -f docker-compose.yml logs -f

seed: ## Seed database with sample data
	cd $(BACKEND_DIR) && python scripts/seed.py

ingest: ## Ingest knowledge documents into ChromaDB
	cd $(BACKEND_DIR) && python scripts/ingest.py

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd $(BACKEND_DIR) && pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=70

test-frontend: ## Run frontend tests
	cd $(FRONTEND_DIR) && npm run test

test-e2e: ## Run Playwright E2E tests
	cd $(FRONTEND_DIR) && npx playwright test

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint + type-check backend
	cd $(BACKEND_DIR) && ruff check app/ tests/ && mypy app/ --ignore-missing-imports

lint-frontend: ## Lint + type-check frontend
	cd $(FRONTEND_DIR) && npm run lint && npm run typecheck

audit: ## Run security audits
	cd $(BACKEND_DIR) && pip-audit -r requirements.txt || true
	cd $(BACKEND_DIR) && bandit -r app/ -ll || true
	cd $(FRONTEND_DIR) && npm audit --audit-level=high || true

format: ## Auto-format code
	cd $(BACKEND_DIR) && ruff format app/ tests/
	cd $(FRONTEND_DIR) && npm run format

migrate: ## Run DB migrations
	cd $(BACKEND_DIR) && alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new MSG="add users table")
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MSG)"

install: ## Install all dependencies
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm install

clean: ## Remove generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	cd $(FRONTEND_DIR) && rm -rf dist node_modules/.cache 2>/dev/null || true

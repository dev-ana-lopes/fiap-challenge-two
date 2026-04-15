.PHONY: help install dev-install lint format test test-cov test-integration migrate migrate-create migrate-down run run-dev compose-up compose-down compose-logs compose-db-shell compose-prod-up compose-prod-down clean build-docker docker-run check

help:
	@echo "Service Order Management API - Make Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install dependencies"
	@echo "  make dev-install      Install with dev dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           Format code with black & isort"
	@echo "  make lint             Run flake8"
	@echo "  make test             Run pytest"
	@echo "  make test-cov         Run pytest with coverage"
	@echo "  make test-integration Run integration tests against a real PostgreSQL"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Apply database migrations"
	@echo "  make migrate-create   Create a new migration"
	@echo "  make migrate-down     Roll back the latest migration"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run API server"
	@echo "  make run-dev          Run API server with reload"
	@echo "  make compose-up       Start local Docker stack"
	@echo "  make compose-down     Stop local Docker stack"
	@echo "  make compose-prod-up  Start production compose stack"
	@echo "  make compose-prod-down Stop production compose stack"
	@echo ""
	@echo "Utilities:"
	@echo "  make build-docker     Build local production image"
	@echo "  make clean            Remove generated artifacts"

install:
	uv sync

dev-install:
	uv sync --dev

format:
	uv run black src tests
	uv run isort src tests

lint:
	uv run black --check src tests
	uv run isort --check-only src tests
	uv run flake8 src tests

test:
	uv run pytest -q

test-cov:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html
	@echo "Coverage reports generated in coverage.xml and htmlcov/index.html"

test-integration:
	INTEGRATION_TESTS_ENABLED=true uv run pytest -q -m integration

migrate:
	uv run alembic -c alembic/alembic.ini upgrade head

migrate-create:
	@read -p "Enter migration name: " name; \
	uv run alembic -c alembic/alembic.ini revision --autogenerate -m "$$name"

migrate-down:
	uv run alembic -c alembic/alembic.ini downgrade -1

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

run-dev:
	uv run uvicorn src.main:app --reload

compose-up:
	docker compose --env-file .env up -d --build
	@echo "Services are running:"
	@echo "  API: http://localhost:8000"
	@echo "  Swagger: http://localhost:8000/docs"
	@echo "  MailHog: http://localhost:8025"

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f api

compose-db-shell:
	docker compose exec postgres psql -U service_order_user -d service_order_db

compose-prod-up:
	docker compose --env-file .env.prod -f docker-compose.prod.yml up -d

compose-prod-down:
	docker compose --env-file .env.prod -f docker-compose.prod.yml down

clean:
	rm -rf .pytest_cache .coverage coverage.xml htmlcov build dist

build-docker:
	docker build -t service-order-api:local .

docker-run:
	docker run -p 8000:8000 \
		-e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/service_order_db" \
		service-order-api:local

check: lint test
	@echo "Checks passed."

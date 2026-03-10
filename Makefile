.PHONY: help install dev-install lint format test migrate run run-dev build compose-up compose-down clean

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
	@echo "  make lint             Run flake8 linter"
	@echo "  make test             Run pytest test suite"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Apply database migrations"
	@echo "  make migrate-create   Create new migration"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run API server (production)"
	@echo "  make run-dev          Run API server (development with reload)"
	@echo "  make compose-up       Start Docker compose services"
	@echo "  make compose-down     Stop Docker compose services"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove build artifacts"
	@echo "  make shell            Activate Poetry virtual environment"
	@echo ""

install:
	poetry install

dev-install:
	poetry install

format:
	poetry run black src tests
	poetry run isort src tests

lint:
	poetry run flake8 src tests

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

migrate:
	poetry run alembic -c alembic/alembic.ini upgrade head

migrate-create:
	@read -p "Enter migration name: " name; \
	poetry run alembic -c alembic/alembic.ini revision --autogenerate -m "$$name"

migrate-down:
	poetry run alembic -c alembic/alembic.ini downgrade -1

run:
	poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000

run-dev:
	poetry run uvicorn src.main:app --reload

compose-up:
	docker compose up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	docker compose exec api poetry run alembic -c alembic/alembic.ini upgrade head
	@echo "Services are running:"
	@echo "  API: http://localhost:8000"
	@echo "  Swagger: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f api

compose-db-shell:
	docker compose exec postgres psql -U service_order_user -d service_order_db

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf build dist *.egg-info

shell:
	poetry shell

update-deps:
	poetry update

lock-deps:
	poetry lock --no-update

show-deps:
	poetry show --tree

build-docker:
	docker build -t service-order-api:1.0.0 .

docker-run:
	docker run -p 8000:8000 \
		-e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/service_order_db" \
		service-order-api:1.0.0

check: format lint test
	@echo "✓ Code formatted"
	@echo "✓ Linting passed"
	@echo "✓ Tests passed"
	@echo ""
	@echo "All checks passed!"

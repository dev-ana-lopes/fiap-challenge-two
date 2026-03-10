# How to run (Docker Compose)

## Prerequisites
- Docker + Docker Compose

## Start the environment
```bash
cp .env.example .env
docker compose up -d --build
```

## Access
- Swagger (OpenAPI UI): `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

## Migrations
Migrations run automatically when the container starts (`MIGRATE_ON_STARTUP=true`).

Run manually (if needed):
```bash
docker compose exec api poetry run alembic -c alembic/alembic.ini upgrade head
```

## Logs and quick troubleshooting
```bash
docker compose ps
docker compose logs -f api
docker compose logs -f postgres
```

## Run tests
Outside Docker (requires local Python/Poetry):
```bash
poetry install
poetry run pytest
```

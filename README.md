# Service Order Management API

API for managing mechanic workshop Service Orders (OS).

## Run locally (Docker Compose)
Prerequisite: Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up -d --build
```

- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

Migrations run automatically on container startup. Manual (if needed):
```bash
docker compose exec api poetry run alembic -c alembic/alembic.ini upgrade head
```

## Documentation
- Index: `docs/README.md`
- Context/scope: `docs/PROJECT_CONTEXT.md`
- How to run: `docs/RUNNING.md`
- Architecture: `docs/ARCHITECTURE.md`
- Postman: `docs/postman/service-order-api.postman_collection.json`

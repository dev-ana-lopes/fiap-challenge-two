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

## Testmail
The application still sends email through the configured `SMTP_*` variables. For live email validation in tests, use Testmail as the destination inbox and configure:

- `TESTMAIL_API_KEY` for the Testmail JSON API
- `TESTMAIL_NAMESPACE` for your inbox namespace
- `TESTMAIL_ENABLED=true` to enable live tests

Use recipients in the format `namespace.tag@inbox.testmail.app`, where `tag` is unique per test run.

SMTP notes:
- `SMTP_USERNAME` is the SMTP login username.
- `SMTP_FROM_EMAIL` is the `From` header used in the message.
- `SMTP_USER` is legacy fallback for authentication compatibility.
- `SMTP_TIMEOUT` is measured in seconds and applies to the SMTP connection.
- When `SMTP_USE_AUTH=false`, the sender can fall back to `no-reply@localhost` for the `From` header in local environments such as MailHog/Mailpit.

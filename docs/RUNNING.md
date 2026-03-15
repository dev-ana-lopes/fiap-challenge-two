# How to run (Docker Compose)

## Prerequisites
- Docker + Docker Compose

## Start the environment
```bash
cp .env.example .env
docker compose up -d --build
```

## Start with MailHog (fake SMTP) for QA
Some endpoints send emails via SMTP. For local QA/testing, you can use MailHog to avoid SMTP failures:
```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.mailhog.yml up -d --build
```

MailHog UI: `http://localhost:8025`

This Compose override also disables SMTP TLS/Auth for QA (`SMTP_USE_TLS=false`, `SMTP_USE_AUTH=false`).

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

## Run live Testmail tests
The default test suite does not depend on Testmail. To enable live email assertions, configure these variables in `.env`:

```bash
TESTMAIL_API_KEY=your-api-key
TESTMAIL_NAMESPACE=your-namespace
TESTMAIL_ENABLED=true
TESTMAIL_API_BASE_URL=https://api.testmail.app/api/json
```

Keep the SMTP configuration pointing to your actual SMTP provider. Then send emails to recipients in the format `namespace.tag@inbox.testmail.app`.

SMTP configuration notes:
- `SMTP_USERNAME` is the username used for SMTP login.
- `SMTP_FROM_EMAIL` controls the `From` header independently from login.
- `SMTP_USER` remains available as a legacy fallback for authentication.
- `SMTP_TIMEOUT` is in seconds and applies to the SMTP connection timeout.
- With `SMTP_USE_AUTH=false`, local tools such as MailHog/Mailpit can run with empty credentials and the app will use a local fallback sender header.

Run only the live tests with:
```bash
poetry run pytest -m testmail
```

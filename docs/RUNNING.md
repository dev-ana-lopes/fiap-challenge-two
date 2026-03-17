# Running The API

## Prerequisites

- Docker and Docker Compose
- Python 3.12 plus Poetry if you want to run tests outside containers

## Start with Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

Useful URLs:
- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

Recommended diagnostics before or after startup:

```bash
docker compose config
docker pull mailhog/mailhog:v1.0.1
```

If `docker pull` fails with DNS or network errors, the host cannot reach Docker Hub. In that case:
- load a previously exported image with `docker load`
- or point Docker to an internal registry mirror that already contains the MailHog image

Migrations run on container startup. Manual execution remains available:

```bash
docker compose exec api poetry run alembic -c alembic/alembic.ini upgrade head
```

## Local email delivery

MailHog is bundled in the default local stack and is the standard SMTP target for demos and QA.

MailHog UI: `http://localhost:8025`

Recommended variables for MailHog:

```bash
APP_BASE_URL=http://localhost:8000
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_FROM_EMAIL=
SMTP_USE_TLS=false
SMTP_USE_AUTH=false
APPROVAL_TOKEN_SECRET=change-me
APPROVAL_TOKEN_TTL_MINUTES=60
```

## Approval flow configuration

Required variables:
- `APP_BASE_URL`: base used in approve/reject links
- `APPROVAL_TOKEN_SECRET`: secret used to sign approval tokens
- `APPROVAL_TOKEN_TTL_MINUTES`: token lifetime

Optional behavior:
- If `APPROVAL_TOKEN_SECRET` is empty, the app falls back to `JWT_SECRET`
- `APP_BASE_URL` should match the externally reachable API URL in QA or production

## Running tests

Install dependencies locally:

```bash
poetry install
```

Run the default suite:

```bash
poetry run pytest -m "not testmail"
```

Run only the API and email end-to-end suite:

```bash
poetry run pytest -m e2e
```

## Live Testmail flow

The default suite does not require Testmail. To validate delivery plus approval-link extraction against a real inbox API, configure:

```bash
TESTMAIL_API_KEY=your-api-key
TESTMAIL_NAMESPACE=your-namespace
TESTMAIL_ENABLED=true
TESTMAIL_API_BASE_URL=https://api.testmail.app/api/json
```

Recipients must use the format `namespace.tag@inbox.testmail.app`.

Run live tests:

```bash
poetry run pytest -m testmail
```

The live tests poll Testmail until the email arrives, extract the approval link, call the public callback endpoint, and assert the final service-order status.

Important: Testmail is used only by the tests. The application runtime still delivers email through SMTP.

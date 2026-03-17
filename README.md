# Service Order Management API

FastAPI application for the Tech Challenge service-order workflow. The project follows Clean Architecture and includes end-to-end budget approval and rejection by email with signed, expiring tokens.

## Phase 2 flow

- Service orders notify the customer whenever they enter `WAITING_APPROVAL`.
- Approval emails contain the service-order id, budget total, budget summary, and dedicated approve/reject links.
- Manual approval remains available through `POST /service-orders/{id}/approval`.
- Public approval by email is available through `GET /public/service-orders/{id}/approval?token=...`.

## Run locally

```bash
cp .env.example .env
docker compose up -d --build
```

Useful URLs:
- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`
- MailHog UI: `http://localhost:8025`

## Docker note

If `docker compose up -d --build` fails while pulling `mailhog/mailhog:v1.0.1`, the issue is Docker host connectivity to Docker Hub, not the API configuration.

Recommended diagnostics:

```bash
docker compose config
docker pull mailhog/mailhog:v1.0.1
```

If the pull fails with DNS or network errors, use one of these options:
- pre-pull the image on a machine with internet and transfer it with `docker save` / `docker load`
- configure Docker to use an internal registry mirror that already has the MailHog image

## Important environment variables

- `APP_BASE_URL`: public base URL used inside approval links
- `APPROVAL_TOKEN_SECRET`: signing secret for approval links
- `APPROVAL_TOKEN_TTL_MINUTES`: link lifetime in minutes
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`, `SMTP_USE_AUTH`, `SMTP_FROM_EMAIL`: local SMTP delivery settings
- `TESTMAIL_*`: live inbox polling settings for Testmail tests only

If `APPROVAL_TOKEN_SECRET` is omitted, the app falls back to `JWT_SECRET`. Production should use a dedicated secret.

`Testmail` is not used to send email in the application runtime. The runtime always delivers by SMTP; locally this SMTP target is MailHog. Testmail is only used by the optional live tests to inspect inbox contents through its API.

## Tests

Default suite:

```bash
poetry install
poetry run pytest -m "not testmail"
```

Live Testmail suite:

```bash
poetry run pytest -m testmail
```

The live suite is skipped unless `TESTMAIL_ENABLED=true`, `TESTMAIL_API_KEY`, and `TESTMAIL_NAMESPACE` are configured.

## Documentation

- `docs/README.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/RUNNING.md`
- `docs/ARCHITECTURE.md`
- `docs/TECH_CHALLENGE.md`
- `docs/postman/README.md`

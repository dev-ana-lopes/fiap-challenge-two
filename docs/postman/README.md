# Postman QA Workspace — Service Order Management API

This folder contains a ready-to-import **Postman Collection** and **Environment** to test the API end-to-end, including negative cases (401/404/409/422/400).

## 1) Start the API with MailHog or your SMTP provider

MailHog is a fake SMTP server used to prevent test failures on endpoints that send emails.

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.mailhog.yml up -d --build
```

Useful URLs:
- API Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`
- MailHog UI (captures outgoing emails): `http://localhost:8025`

Notes:
- `docker-compose.mailhog.yml` disables SMTP TLS/Auth for QA (`SMTP_USE_TLS=false`, `SMTP_USE_AUTH=false`).
- In the current SMTP setup, login and sender are separate concerns:
  - `SMTP_USERNAME` is used for SMTP authentication.
  - `SMTP_FROM_EMAIL` controls the `From` header.
  - `SMTP_USER` remains only as a legacy fallback for auth compatibility.
  - `SMTP_TIMEOUT` is in seconds and applies to the SMTP connection.
- With MailHog/Mailpit and `SMTP_USE_AUTH=false`, empty SMTP credentials are valid and the app can use `no-reply@localhost` as a local `From` fallback.
- If you want Postman requests to generate inboxes on Testmail, set the Postman environment variable `testmail_namespace`. The collection will then generate emails like `namespace.tag@inbox.testmail.app` automatically.

## 2) Import into Postman

Import both files:
- `docs/postman/ServiceOrderAPI.postman_collection.json`
- `docs/postman/ServiceOrderAPI.local.postman_environment.json`

Select the environment **ServiceOrderAPI Local**.

Optional environment variables for Testmail:
- `testmail_namespace`: when set, generated `user_email`, `service_order_customer_email`, `customer_crud_email`, and `customer_crud_updated_email` use `@inbox.testmail.app`.

Suggested local `.env` for MailHog/Mailpit:
```bash
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_USE_TLS=false
SMTP_USE_AUTH=false
SMTP_TIMEOUT=10
```

## 3) Recommended execution order

The collection is stateful (it saves IDs/tokens into variables). Run in order:
1. `00 - Health`
2. `10 - Auth`
3. `20 - Setup (Admin Data)`
4. `30 - Service Orders (Secure)`
5. Other folders as needed (`40+`)

Notes:
- Secure folders use collection-level Bearer token: `{{access_token}}`.
- Public endpoints disable auth explicitly.

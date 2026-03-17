# Architecture

## Architectural style

The codebase follows Clean Architecture:

- `src/domain`: entities, enums, errors, repository contracts, email and token ports
- `src/application`: use cases that orchestrate service-order flows
- `src/infrastructure`: PostgreSQL repositories, SMTP sender, JWT services, settings
- `src/presentation`: FastAPI routes, request and response schemas, dependency wiring

Routes do not contain business rules. They translate HTTP requests into use-case calls and map domain or application errors to HTTP responses.

## Approval by email design

### Ports introduced or reinforced

- `EmailSender`: notification contract used by create, status-update, and approval flows
- `ApprovalTokenService`: token generation and validation contract for public approval links

### Infrastructure implementations

- `SmtpEmailSender`: builds the approval email template and public approve or reject URLs using `APP_BASE_URL`
- `JwtApprovalTokenService`: signs approval tokens with expiration using `APPROVAL_TOKEN_SECRET`

For local development, the SMTP provider is MailHog. Testmail is not part of runtime delivery; it is only used by the optional live suite to poll inbox contents by API.

### Shared approval workflow

1. A service order reaches `WAITING_APPROVAL`
2. `SendApprovalRequestEmailUseCase` generates an approve token and a reject token
3. The SMTP adapter composes an email with:
   - service-order id
   - budget total
   - budget summary
   - approve link
   - reject link
4. The public callback validates the token and delegates to the same decision use case used by manual approval

## Security decisions

- Approval links use signed tokens instead of predictable query parameters
- Tokens include the service-order id, decision, purpose, and expiration
- The public callback checks:
  - invalid signature or malformed payload
  - expired token
  - token and service-order mismatch
  - already processed approval decision

## Status rules

The domain entity `ServiceOrder` owns the transition map. Relevant transitions for the phase-2 flow:

- `RECEIVED -> DIAGNOSIS | WAITING_APPROVAL | CANCELLED`
- `DIAGNOSIS -> WAITING_APPROVAL | IN_PROGRESS | CANCELLED`
- `WAITING_APPROVAL -> IN_PROGRESS | CANCELLED`
- `IN_PROGRESS -> FINISHED | CANCELLED`
- `FINISHED -> DELIVERED`

Budget rejection is explicitly documented as `WAITING_APPROVAL -> CANCELLED`.

## Main runtime flows

### Create service order

`POST /service-orders` creates the aggregate in `WAITING_APPROVAL`, persists items, and tries to send the approval email. Email-delivery failure is logged but does not roll back order creation.

### Manual approval

`POST /service-orders/{id}/approval` is authenticated and accepts a payload with `approved: true|false`.

### Email approval callback

`GET /public/service-orders/{id}/approval?token=...` is public, validates the token, and applies the decision.

### Generic status update

`PATCH /service-orders/{id}/status` uses the same domain transition rules. When the target status is `WAITING_APPROVAL`, it sends the approval email instead of a generic status-change email.

## Observability

The implementation logs:

- approval-token generation
- approval-token validation failures
- email sending attempts
- approval and rejection actions
- email-delivery failures during service-order creation

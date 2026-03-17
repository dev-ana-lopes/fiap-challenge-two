# Tech Challenge Mapping

## Scope covered in this repository

- Clean Architecture organization across `domain`, `application`, `infrastructure`, and `presentation`
- JWT-protected operational endpoints
- External budget approval and rejection through email
- Status tracking and public status consultation
- Dockerized execution with PostgreSQL and MailHog support
- Automated unit, integration, end-to-end, and live Testmail scenarios

## Phase 2 deliverable highlights

- Approval email sent whenever a service order enters `WAITING_APPROVAL`
- Secure approve and reject links with signed tokens and expiration
- Public callback endpoint for customer decision
- Manual approval endpoint preserved for compatibility
- Testmail polling helpers and live email-flow tests
- Updated Postman collection and environment
- MailHog-first local runtime, with Testmail restricted to live validation

## Testing strategy

- Unit: domain transitions, approval-token generation and validation, email composition
- Integration: API routes with dependency overrides, manual approval, public callback, error cases
- End-to-end: create order, send email, capture token or live email, apply approval link, assert final status

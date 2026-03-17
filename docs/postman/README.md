# Postman QA Workspace

The collection covers the secure service-order endpoints and the public approval callback introduced for phase 2.

## Recommended local setup

```bash
cp .env.example .env
docker compose up -d --build
```

Useful URLs:
- Swagger: `http://localhost:8000/docs`
- MailHog: `http://localhost:8025`

## Files

- `docs/postman/ServiceOrderAPI.postman_collection.json`
- `docs/postman/ServiceOrderAPI.local.postman_environment.json`
- `docs/postman/ServiceOrderAPI.email-approval.postman_collection.json`
- `docs/postman/ServiceOrderAPI.email-approval.local.postman_environment.json`

## Environment variables in Postman

- `base_url`
- `access_token`
- `service_order_id`
- `service_order_id_manual_approve`
- `service_order_id_manual_reject`
- `service_order_id_status_update`
- `service_order_id_public_approval`
- `approval_email_token`
- `approval_email_link`
- `testmail_namespace`
- `vehicle_customer_email`
- `vehicle_customer_id`

`approval_email_token` and `approval_email_link` are manual helper variables. Fill them from MailHog or Testmail when you want to call the public approval callback directly from Postman.

## Recommended execution order

1. `00 - Health`
2. `10 - Auth`
3. `20 - Setup (Admin Data)`
4. `30 - Service Orders (Secure)`
5. Open MailHog/Testmail, copy the token for `service_order_id_public_approval`
6. Set `approval_email_token`
7. `40 - Public`

The collection is organized for sequential execution. Manual approve, manual reject, public approval, and status update now use different service-order ids so one scenario does not invalidate the next.

## Email approval note

The collection does not fetch the email automatically. The intended local flow is:

1. Create the service order
2. Open MailHog or Testmail
3. Copy the approval link or token from the email
4. Paste it into `approval_email_link` or `approval_email_token`
5. Call the public approval request in folder `40 - Public`

Local use:
- MailHog is the normal source for the approval email in local runs
- the request `GET /public/service-orders/{{service_order_id_public_approval}}/approval?token={{approval_email_token}}` will fail early with a clear message if the token was not filled

Runner note:
- the public callback remains manual by design
- all other requests are structured to run in order in Postman Runner/Newman without reusing the same terminal service-order state

## Vehicles folder note

The folder `60 - Vehicles` is self-contained:
- it creates its own support customer and stores the id in `vehicle_customer_id`
- it uses `vehicle_customer_email` for that setup customer
- it does not depend on `50 - Customers (Secure)` or on `customer_id_customers_crud`

This allows the vehicles flow to run in isolation or as part of the full runner sequence without stale customer ids causing `POST /vehicles` to fail with `404`.

## Focused email approval collection

If you want only the manual email-approval scenario, use:
- `docs/postman/ServiceOrderAPI.email-approval.postman_collection.json`
- `docs/postman/ServiceOrderAPI.email-approval.local.postman_environment.json`

Recommended order:
1. `00 - Health`
2. `10 - Auth`
3. `20 - Email Approval -> POST /service-orders`
4. Open MailHog or Testmail and copy the approval token
5. Set `approval_email_token`
6. Run the manual approval request
7. Run the final public status check

This focused collection avoids the rest of the QA suite and is intended only for the budget approval by email demo flow.

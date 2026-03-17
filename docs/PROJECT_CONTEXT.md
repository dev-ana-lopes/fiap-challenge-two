# Project Context

## Overview

This repository implements the backend for a mechanic workshop service-order system. The phase-2 scope adds external budget approval through email without breaking the existing authenticated approval endpoint.

## Main business goals

- Centralize service-order creation, tracking, and customer communication
- Enforce explicit status transitions inside the domain layer
- Allow a customer to approve or reject a budget from an email link
- Keep the API testable, containerized, and demonstrable for the Tech Challenge

## Current status model

The workflow is explicitly modeled as:

`RECEIVED -> DIAGNOSIS -> WAITING_APPROVAL -> IN_PROGRESS -> FINISHED -> DELIVERED`

Cancellation is allowed from the active stages covered by the domain rules. Rejection of a budget moves the order from `WAITING_APPROVAL` to `CANCELLED`.

## Approval channels

The project now supports two approval paths:

- Authenticated manual decision: `POST /service-orders/{id}/approval`
- Public email callback: `GET /public/service-orders/{id}/approval?token=...`

Both paths reuse the same application logic and the same domain transition rule.

## Main endpoints

- `POST /service-orders`
- `GET /service-orders`
- `GET /service-orders/{id}/status`
- `POST /service-orders/{id}/approval`
- `PATCH /service-orders/{id}/status`
- `GET /public/service-orders/{id}/status`
- `GET /public/service-orders/{id}/approval?token=...`

## Out of scope

- Frontend or customer portal
- Payment capture
- Supplier and full inventory operations
- Fine-grained authorization and user roles

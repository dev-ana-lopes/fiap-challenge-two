# Project context — Service Order Management API

## Overview
Backend API for managing mechanic workshop **Service Orders (OS)**: intake, service/parts items, status tracking, and customer communication.

## Problem statement
Managing service orders via spreadsheets/WhatsApp typically leads to:
- poor status traceability (Received → Diagnosis → Waiting approval → In progress → Finished → Delivered);
- inconsistent approval workflow;
- fragmented history by customer/vehicle;
- little to no automated communication.

## Objectives
- Centralize service order creation and tracking.
- Enforce controlled status transitions.
- Register services and parts linked to each order.
- Notify customers by email on workflow events.
- Protect endpoints with JWT authentication.

## Scope
In scope:
- authentication via `POST /auth/login` (JWT);
- service orders: create, list active, check status, approve/reject, update status.

Out of scope (for now):
- UI/Frontend, payments/billing, full user management (roles/permissions), inventory/suppliers.

## Main endpoints
- `GET /health` — healthcheck
- `POST /auth/login` — authenticate and issue JWT
- `POST /service-orders` — open a new service order
- `GET /service-orders` — list active service orders
- `GET /service-orders/{id}/status` — get order status
- `POST /service-orders/{id}/approval` — register approval/rejection
- `PATCH /service-orders/{id}/status` — update order status

## Technology
Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Pydantic, JWT, SMTP, Docker Compose.

## How to run
See `docs/RUNNING.md`.

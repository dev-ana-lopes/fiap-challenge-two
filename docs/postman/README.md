# Postman

Arquivos:

- `ServiceOrderAPI.postman_collection.json`
- `ServiceOrderAPI.local.postman_environment.json`

## Como usar

1. importe a collection
2. importe o environment local
3. ajuste apenas `base_url`
4. rode a collection inteira no Runner ou, se preferir, a sequencia `Health -> Auth -> Customers -> Vehicles -> Catalog -> Service Orders -> Metrics`

## O que a collection automatiza

- gera credenciais e dados unicos por execucao
- salva `access_token` automaticamente apos `POST /auth/login`
- salva `customer_id`, `vehicle_id`, `service_id`, `part_id` e `service_order_id` automaticamente
- evita conflitos de reexecucao para usuario, cliente, veiculo e catalogo

## Variaveis que continuam opcionais

- `approval_token`

Use `approval_token` apenas para os endpoints publicos de aprovacao. Esse valor nao e capturado automaticamente pela collection porque depende do fluxo de email.

## Fluxo esperado

1. `GET /health`
2. `POST /auth/register`
3. `POST /auth/login`
4. `POST /customers`
5. `POST /vehicles`
6. `POST /catalog/services`
7. `POST /catalog/parts`
8. `POST /service-orders`
9. `GET /service-orders/{id}`
10. `POST /service-orders/{id}/approval`
11. `PATCH /service-orders/{id}/status`
12. `GET /metrics/average-execution-time`

O Swagger em `/docs` e a collection usam as mesmas rotas finais.

# Fluxos, Inventário e Evidências

## Inventário de endpoints

### Saúde e operação

- `GET /health`
- `GET /health/live`
- `GET /health/ready`

### Autenticação

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

### Clientes

- `POST /customers`
- `GET /customers`
- `GET /customers/{customer_id}`
- `PUT /customers/{customer_id}`
- `DELETE /customers/{customer_id}`

### Veículos

- `POST /vehicles`
- `GET /vehicles`
- `GET /vehicles/{vehicle_id}`
- `PUT /vehicles/{vehicle_id}`
- `DELETE /vehicles/{vehicle_id}`

### Catálogo

- `POST /catalog/services`
- `GET /catalog/services`
- `GET /catalog/services/{service_id}`
- `PUT /catalog/services/{service_id}`
- `DELETE /catalog/services/{service_id}`
- `POST /catalog/parts`
- `GET /catalog/parts`
- `GET /catalog/parts/{part_id}`
- `PUT /catalog/parts/{part_id}`
- `DELETE /catalog/parts/{part_id}`

### ServiceOrder

- `POST /service-orders`
- `GET /service-orders`
- `GET /service-orders/active`
- `GET /service-orders/{id}`
- `GET /service-orders/{id}/status`
- `PATCH /service-orders/{id}/status`
- `POST /service-orders/{id}/approval`

### Públicos

- `GET /public/service-orders/{id}/status`
- `GET /public/service-orders/{id}/approval`
- `POST /public/service-orders/{id}/approval`

### Métricas

- `GET /metrics/average-execution-time`

## Inventário de entidades e agregado

- `Customer`
- `Vehicle`
- `CatalogService`
- `InventoryPart`
- `ServiceItem`
- `PartItem`
- `ServiceOrder`
- `User`

Agregado principal:

- `ServiceOrder`

Status válidos:

- `RECEIVED`
- `DIAGNOSIS`
- `WAITING_APPROVAL`
- `IN_PROGRESS`
- `FINISHED`
- `DELIVERED`

## Inventário de casos de uso

- `AuthenticateUserUseCase`
- `RegisterUserUseCase`
- `CreateCustomerUseCase`
- `UpdateCustomerUseCase`
- `DeleteCustomerUseCase`
- `GetCustomerUseCase`
- `ListCustomersUseCase`
- `CreateVehicleUseCase`
- `UpdateVehicleUseCase`
- `DeleteVehicleUseCase`
- `GetVehicleUseCase`
- `ListVehiclesUseCase`
- `CreateCatalogServiceUseCase`
- `UpdateCatalogServiceUseCase`
- `DeleteCatalogServiceUseCase`
- `ListCatalogServicesUseCase`
- `GetCatalogServiceUseCase`
- `CreateInventoryPartUseCase`
- `UpdateInventoryPartUseCase`
- `DeleteInventoryPartUseCase`
- `ListInventoryPartsUseCase`
- `GetInventoryPartUseCase`
- `CreateServiceOrderUseCase`
- `ApproveServiceOrderUseCase`
- `ApplyServiceOrderApprovalDecisionUseCase`
- `ApproveServiceOrderByTokenUseCase`
- `ListServiceOrdersUseCase`
- `ListActiveServiceOrdersUseCase`
- `GetServiceOrderStatusUseCase`
- `GetServiceOrderDetailsUseCase`
- `UpdateServiceOrderStatusUseCase`
- `SendApprovalRequestEmailUseCase`
- `GetAverageExecutionTimeUseCase`

## Inventário de testes

- `tests/test_auth_and_admin_api.py`
- `tests/test_service_order_api.py`
- `tests/test_domain_rules.py`
- `tests/test_validation.py`
- `tests/test_approval_token_service.py`
- `tests/test_database_url_utils.py`
- `tests/test_settings_and_health.py`
- `tests/test_smtp_client.py`
- `tests/test_service_order_email_approval_testmail.py`
- `tests/test_testmail_integration.py`
- `tests/test_use_case_edges.py`

## Inventário de migrations

- `001_initial.py`
- `002_phase1_catalog_and_fields.py`
- `003_phase2_service_order_decision_fields.py`

## Integrações externas

- PostgreSQL
- Alembic
- SMTP
- MailHog
- Testmail opcional
- JWT
- Docker Compose
- GitHub Actions
- AWS EC2, RDS e ECR

## Assets de infraestrutura

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `scripts/docker/entrypoint.sh`
- `scripts/deploy/bootstrap_ec2.sh`
- `scripts/deploy/release.sh`
- `.github/workflows/ci-cd.yml`
- `infra/*.tf`
- `k8s/*.yaml`

## Fluxo funcional principal

### Criação da OS

1. autenticar via JWT
2. garantir cliente e veículo
3. informar serviços e peças
4. reduzir estoque
5. salvar OS
6. enviar email para aprovação

### Aprovação

1. gerar token assinado
2. validar expiração e vínculo da OS
3. aplicar decisão
4. notificar mudança de status

### Deploy

1. validar repositório no CI
2. buildar imagem
3. publicar opcionalmente
4. aplicar release em EC2
5. rodar migration
6. validar `/health/ready`

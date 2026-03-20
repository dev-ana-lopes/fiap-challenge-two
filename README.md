# Tech Challenge Workshop Service Orders API

API backend monolítica em FastAPI para gestão de ordens de serviço de oficina mecânica. A solução cobre clientes, veículos, catálogo de serviços, peças/insumos, orçamento, aprovação por email, evolução de status da OS, métricas, containers, Kubernetes, Terraform e pipeline CI/CD.

## Objetivos das Fases 1 e 2

- Fase 1: autenticação JWT, validações brasileiras, CRUDs administrativos, abertura e acompanhamento de OS, orçamento automático, email e testes.
- Fase 2: refatoração com Clean Architecture, fluxo de aprovação externa, listagem ativa com ordenação por prioridade, artefatos de deploy e documentação final.

## Arquitetura

Visão em camadas:

- `src/domain`: entidades, enums, validações, erros e contratos.
- `src/application`: casos de uso e DTOs.
- `src/infrastructure`: PostgreSQL/Alembic, SMTP, JWT, configurações.
- `src/presentation`: rotas FastAPI, dependências HTTP e schemas.

Fluxo principal de OS:

1. autenticação administrativa via JWT;
2. cadastro de cliente, veículo, serviço e peça;
3. abertura da OS com `customer_id`, `vehicle_id`, `service_ids` e `part_refs`;
4. cálculo automático do orçamento;
5. envio de email com tokens de aprovação/reprovação;
6. aprovação manual, por link de email ou por notificação externa;
7. atualização de status e cálculo de tempo médio de execução.

Mais detalhes em [docs/ARCHITECTURE.md](/c:/fiap-challenge-two/docs/ARCHITECTURE.md).

## Componentes da solução

- API FastAPI com Swagger/OpenAPI em `/docs`
- PostgreSQL com Alembic
- SMTP local com MailHog
- Tokens JWT para autenticação administrativa
- Tokens assinados para aprovação pública do orçamento
- Dockerfile e `docker-compose`
- manifests Kubernetes em [k8s](/c:/fiap-challenge-two/k8s)
- Terraform em [infra](/c:/fiap-challenge-two/infra)
- pipeline CI/CD em [.github/workflows/ci-cd.yml](/c:/fiap-challenge-two/.github/workflows/ci-cd.yml)

## Endpoints finais

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`
- `GET|POST|PUT|DELETE /customers`
- `GET|POST|PUT|DELETE /vehicles`
- `GET|POST|PUT|DELETE /catalog/services`
- `GET|POST|PUT|DELETE /catalog/parts`
- `POST /service-orders`
- `GET /service-orders`
- `GET /service-orders/active`
- `GET /service-orders/{id}`
- `GET /service-orders/{id}/status`
- `PATCH /service-orders/{id}/status`
- `POST /service-orders/{id}/approval`
- `GET /public/service-orders/{id}/status`
- `GET /public/service-orders/{id}/approval?token=...`
- `POST /public/service-orders/{id}/approval`
- `GET /metrics/average-execution-time`

## Estrutura de pastas

```text
src/
  application/
  domain/
  infrastructure/
  presentation/
alembic/
docs/
  postman/
infra/
k8s/
tests/
```

## Banco e migrations

Banco escolhido: PostgreSQL.

Justificativa:

- aderente ao enunciado original;
- bom suporte a integridade relacional para cliente, veículo, catálogo e OS;
- compatível com Alembic, Docker Compose, RDS e EKS.

Executar migrations localmente:

```bash
poetry run alembic -c alembic/alembic.ini upgrade head
```

## Execução local

Via Docker Compose:

```bash
cp .env.example .env
docker compose up -d --build
```

URLs úteis:

- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`
- MailHog: `http://localhost:8025`

Via Poetry:

```bash
poetry install
poetry run uvicorn src.main:app --reload
```

## Variáveis de ambiente

Principais variáveis:

- `DATABASE_URL`
- `ENVIRONMENT`
- `APP_BASE_URL`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_FROM_EMAIL`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_USE_AUTH`
- `SMTP_TIMEOUT_SECONDS`
- `APPROVAL_TOKEN_SECRET`
- `APPROVAL_TOKEN_TTL_MINUTES`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXPIRATION_MINUTES`
- `MIGRATE_ON_STARTUP`
- `TESTMAIL_API_KEY`
- `TESTMAIL_NAMESPACE`
- `TESTMAIL_ENABLED`

Referência completa em [.env.example](/c:/fiap-challenge-two/.env.example).

## Email

Fluxos cobertos:

- envio do orçamento ao entrar em `WAITING_APPROVAL`;
- envio de atualização de status para o cliente;
- QA local com MailHog;
- testes live opcionais com Testmail.

Rodar com MailHog:

```bash
docker compose up -d mailhog
```

Habilitar Testmail:

```bash
TESTMAIL_ENABLED=true
TESTMAIL_API_KEY=...
TESTMAIL_NAMESPACE=...
```

Os testes live continuam opcionais. Em runtime a aplicação sempre envia por SMTP.

## Testes

Suite padrão:

```bash
poetry run pytest -q
```

Cobertura dos módulos críticos:

```bash
poetry run pytest --cov=src/application --cov=src/domain --cov=src/presentation/api/routes --cov=src/infrastructure/email --cov-report=term -m "not testmail"
```

Última medição obtida: `85%`.

Checagens básicas:

```bash
poetry run black --check src tests
poetry run isort --check-only src tests
poetry run flake8 src tests
```

## Docker e Compose

- [Dockerfile](/c:/fiap-challenge-two/Dockerfile): build multi-stage com healthcheck em `/health`
- [docker-compose.yml](/c:/fiap-challenge-two/docker-compose.yml): stack local completa
- [docker-compose.prod.yml](/c:/fiap-challenge-two/docker-compose.prod.yml): execução produtiva com job de migration separado

## Kubernetes

Manifestos disponíveis em [k8s](/c:/fiap-challenge-two/k8s):

- [deployment.yaml](/c:/fiap-challenge-two/k8s/deployment.yaml)
- [service.yaml](/c:/fiap-challenge-two/k8s/service.yaml)
- [configmap.yaml](/c:/fiap-challenge-two/k8s/configmap.yaml)
- [secret.yaml](/c:/fiap-challenge-two/k8s/secret.yaml)
- [hpa.yaml](/c:/fiap-challenge-two/k8s/hpa.yaml)

Deploy:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

## Terraform

Provisionamento em [infra](/c:/fiap-challenge-two/infra):

- VPC
- EKS
- RDS PostgreSQL

Comandos:

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## CI/CD

Pipeline em [ci-cd.yml](/c:/fiap-challenge-two/.github/workflows/ci-cd.yml) com:

- instalação das dependências;
- lint;
- testes com cobertura;
- build da imagem Docker;
- push para ECR;
- `terraform apply`;
- aplicação dos manifestos Kubernetes.

## Postman

- collection: [docs/postman/ServiceOrderAPI.postman_collection.json](/c:/fiap-challenge-two/docs/postman/ServiceOrderAPI.postman_collection.json)
- environment local: [docs/postman/ServiceOrderAPI.local.postman_environment.json](/c:/fiap-challenge-two/docs/postman/ServiceOrderAPI.local.postman_environment.json)
- instruções: [docs/postman/README.md](/c:/fiap-challenge-two/docs/postman/README.md)

## Deploy na AWS — pré-requisitos e passos manuais

As ações abaixo precisam ser feitas manualmente antes do deploy final:

1. Criar repositório no Amazon ECR
   criar o repositório da imagem;
   registrar a URI;
   configurar permissões de push/pull.
2. Criar banco no Amazon RDS PostgreSQL
   criar instância;
   configurar database, usuário e senha;
   ajustar security groups;
   registrar endpoint e porta.
3. Criar cluster no Amazon EKS
   configurar VPC e subnets;
   criar cluster;
   criar node group;
   validar acesso `kubectl`.
4. Configurar email e segredos
   configurar SMTP ou Amazon SES;
   criar credenciais;
   armazenar segredos;
   configurar variáveis da aplicação.
5. Expor a aplicação e conectar pipeline
   configurar ingress/load balancer;
   configurar DNS, se aplicável;
   configurar credenciais do pipeline;
   executar deploy inicial e validar healthcheck, docs, banco e email.

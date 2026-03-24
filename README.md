# Tech Challenge Workshop Service Orders API

Backend monolítico em FastAPI para gestão de ordens de serviço de oficina mecânica, organizado em Clean Architecture e preparado para execução local com Docker Compose.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2 + Alembic
- SMTP (MailHog no local)
- Docker Compose
- GitHub Actions
- Terraform para `EC2 + RDS`

## Arquitetura

Camadas principais:

- `src/domain`: entidades, enums, contratos e regras de negócio
- `src/application`: casos de uso
- `src/infrastructure`: banco, email, JWT, logging e settings
- `src/presentation`: rotas HTTP, schemas e dependências

Agregado principal:

- `ServiceOrder`

Documentação complementar:

- [README.deploy.md](/c:/fiap-challenge-two/README.deploy.md)
- [solution-architecture.md](/c:/fiap-challenge-two/docs/architecture/solution-architecture.md)
- [flows.md](/c:/fiap-challenge-two/docs/architecture/flows.md)
- [ADR-001-arquitetura-e-estrategia-de-deploy.md](/c:/fiap-challenge-two/docs/adr/ADR-001-arquitetura-e-estrategia-de-deploy.md)

## Pré-requisitos

- Docker Desktop com Compose v2
- Python 3.12
- Poetry 1.7+
- `make` opcional

## Variáveis de ambiente

Crie o arquivo local a partir do exemplo:

```bash
cp .env.example .env
```

Principais variáveis:

- `DATABASE_URL`
- `APP_BASE_URL`
- `JWT_SECRET`
- `APPROVAL_TOKEN_SECRET`
- `SMTP_HOST`
- `SMTP_FROM_EMAIL`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`

O carregamento é validado em runtime. Em `staging/production`, o app rejeita:

- segredos fracos ou placeholders
- `SMTP_HOST=localhost/mailhog`
- `CORS_ALLOWED_ORIGINS=*`
- `APP_BASE_URL` de placeholder

Também há suporte a `*_FILE` para segredos como `JWT_SECRET_FILE`, `APPROVAL_TOKEN_SECRET_FILE` e `SMTP_PASSWORD_FILE`.

## Como subir com Make e Docker Compose

Subida local:

```bash
make compose-up
```

Sem `make`:

```bash
docker compose --env-file .env up -d --build
```

Serviços:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/health/ready`
- MailHog: `http://localhost:8025`

## Migrations

Local:

```bash
make migrate
```

Container:

```bash
docker compose exec api alembic -c alembic/alembic.ini upgrade head
```

## Testes

Suite padrão:

```bash
make test
```

Cobertura:

```bash
make test-cov
```

## Lint e formatação

```bash
make lint
make format
```

## Swagger e APIs principais

Autenticação:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

Cadastros administrativos:

- `GET|POST|PUT|DELETE /customers`
- `GET|POST|PUT|DELETE /vehicles`
- `GET|POST|PUT|DELETE /catalog/services`
- `GET|POST|PUT|DELETE /catalog/parts`

Ordens de serviço:

- `POST /service-orders`
- `GET /service-orders`
- `GET /service-orders/active`
- `GET /service-orders/{id}`
- `GET /service-orders/{id}/status`
- `PATCH /service-orders/{id}/status`
- `POST /service-orders/{id}/approval`

Endpoints públicos:

- `GET /public/service-orders/{id}/status`
- `GET /public/service-orders/{id}/approval`
- `POST /public/service-orders/{id}/approval`

Operação:

- `GET /health`
- `GET /health/live`
- `GET /health/ready`

## MailHog

O ambiente local usa:

- SMTP: `mailhog:1025`
- UI: `http://localhost:8025`

Emails esperados:

- solicitação de aprovação do orçamento
- atualização de status da OS

## Troubleshooting básico

- Se `/health/ready` retornar `503`, valide se o `postgres` está saudável.
- Se o container da API reiniciar, confira `DATABASE_URL`, `JWT_SECRET` e `APPROVAL_TOKEN_SECRET`.
- Se o email não sair no local, valide `SMTP_HOST=mailhog`, `SMTP_PORT=1025` e a UI do MailHog.
- Se o Compose falhar com env faltando, compare seu arquivo com [.env.example](/c:/fiap-challenge-two/.env.example).

Troubleshooting detalhado:

- [troubleshooting.md](/c:/fiap-challenge-two/docs/runbooks/troubleshooting.md)

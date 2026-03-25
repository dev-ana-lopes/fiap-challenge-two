# Deploy legado com EC2 + Docker Compose

Este documento foi mantido como fallback operacional. O caminho principal da Fase 2 é `k3s + Terraform`, documentado no `README.md`, mas o fluxo legado com Docker Compose continua disponível para transição controlada.

## Quando usar

- recuperação de um ambiente antigo baseado em Compose;
- comparação entre a estratégia nova e o deploy anterior;
- banca pedindo demonstração explícita do fluxo legado preservado.

## Estratégia

- build local da imagem na EC2;
- `docker-compose.prod.yml` com serviço `migrate` + `api`;
- validação de `.env.prod` com `scripts/deploy/prepare_env.py`;
- healthcheck em `/health/ready`.

## Pré-requisitos

- EC2 Linux com Docker e Docker Compose
- PostgreSQL acessível pela EC2
- arquivo `.env.prod` criado a partir de `.env.prod.example`
- security group com `8000` aberto se o fallback Compose for exposto

## Passo a passo

### 1. Preparar o host

```bash
chmod +x scripts/deploy/bootstrap_ec2.sh
./scripts/deploy/bootstrap_ec2.sh
```

### 2. Preparar o ambiente

```bash
cp .env.prod.example .env.prod
python3 scripts/deploy/prepare_env.py .env.prod
```

Preencher obrigatoriamente:

- `DATABASE_URL`
- `APP_BASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`
- `JWT_SECRET` ou `JWT_SECRET_FILE`
- `APPROVAL_TOKEN_SECRET` ou `APPROVAL_TOKEN_SECRET_FILE`

Se `EMAIL_PROVIDER=SMTP`, preencher também:

- `SMTP_HOST`
- `SMTP_FROM_EMAIL`
- `SMTP_USERNAME`
- `SMTP_PASSWORD` ou `SMTP_PASSWORD_FILE`

### 3. Executar release

```bash
chmod +x scripts/deploy/release.sh
API_IMAGE=service-order-api:local ./scripts/deploy/release.sh
```

## Pipeline

O workflow `.github/workflows/ci-cd.yml` preserva esse caminho no `workflow_dispatch` com:

- `deployment_target=compose-legacy`

Esse job continua usando o runner self-hosted existente, para não quebrar o fluxo anterior.

## Validação

```bash
curl http://<host>:8000/health
curl http://<host>:8000/health/ready
curl http://<host>:8000/docs
```

## Transição recomendada

- usar o fallback Compose apenas enquanto necessário;
- manter novas demonstrações e documentação centradas no fluxo `k3s`;
- desligar a porta `8000` no Terraform quando o fallback não for mais necessário.

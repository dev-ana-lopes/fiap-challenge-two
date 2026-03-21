# README de Deploy

Guia de deploy para `EC2 + RDS` com Docker Compose, mantendo Kubernetes apenas como evolução futura.

## Estratégia adotada

- Build da imagem Docker localmente ou no CI
- Publicação opcional em registry
- Execução da aplicação em uma `EC2`
- PostgreSQL gerenciado em `RDS`
- Migrations executadas pelo serviço `migrate` antes da API

## Pré-requisitos

- EC2 Linux com Docker e Docker Compose
- RDS PostgreSQL acessível pela EC2
- Arquivo `.env.prod` criado a partir de [.env.prod.example](/c:/fiap-challenge-two/.env.prod.example)
- Security Groups liberando:
  - `22` para administração
  - `8000` para acesso à API
  - `5432` da EC2 para o RDS

## Bootstrap da EC2

No host recém-criado:

```bash
chmod +x scripts/deploy/bootstrap_ec2.sh
./scripts/deploy/bootstrap_ec2.sh
```

## Montagem do ambiente de produção

```bash
cp .env.prod.example .env.prod
```

Preencher obrigatoriamente:

- `DATABASE_URL`
- `APP_BASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`
- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD` ou `SMTP_PASSWORD_FILE`
- `SMTP_FROM_EMAIL`
- `JWT_SECRET` ou `JWT_SECRET_FILE`
- `APPROVAL_TOKEN_SECRET` ou `APPROVAL_TOKEN_SECRET_FILE`

## Fluxo de deploy manual

Build local na EC2:

```bash
docker build -t service-order-api:local .
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Ou usando imagem publicada:

```bash
API_IMAGE=123456789012.dkr.ecr.sa-east-1.amazonaws.com/service-order-api:<tag> \
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

## Fluxo de release recomendado

```bash
chmod +x scripts/deploy/release.sh
API_IMAGE=service-order-api:local ./scripts/deploy/release.sh
```

O script:

1. executa migrations
2. sobe a API
3. mostra o estado do compose

## GitHub Actions

O workflow em [.github/workflows/ci-cd.yml](/c:/fiap-challenge-two/.github/workflows/ci-cd.yml) faz:

- `validate`: lint + testes + cobertura
- `build-image`: build local da imagem
- `publish-image`: push opcional para ECR
- `deploy-ec2`: deploy controlado por `workflow_dispatch`

Segredos esperados para deploy automatizado:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REGISTRY`
- `ECR_REPOSITORY`
- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_PRIVATE_KEY`
- `APP_ENV_PROD`

## Estratégia de segredos

- Local: `.env`
- Produção: `.env.prod` fora do versionamento ou arquivos montados via `*_FILE`
- Evolução AWS: usar `SSM Parameter Store` ou `Secrets Manager` para renderizar `APP_ENV_PROD` no pipeline, sem mudar o contrato da aplicação

## Validações pós-deploy

```bash
curl http://<host>:8000/health
curl http://<host>:8000/health/ready
curl http://<host>:8000/docs
```

Runbook detalhado:

- [deploy-ec2-rds.md](/c:/fiap-challenge-two/docs/runbooks/deploy-ec2-rds.md)

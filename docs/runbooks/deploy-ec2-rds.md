# Runbook de Deploy em EC2 + RDS

## Objetivo

Subir a aplicação em uma EC2 com Docker Compose usando PostgreSQL no RDS.

## Pré-requisitos

- Infra criada pelo Terraform em `infra/`
- Acesso SSH à EC2
- Repositório disponível na EC2
- `.env.prod` preenchido
- Imagem local (`service-order-api:local`) ou imagem publicada em registry

## Passo a passo

### 1. Provisionar infraestrutura

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

### 2. Conectar na EC2

```bash
ssh -i <key>.pem ec2-user@<ec2_public_ip>
```

### 3. Bootstrap do host

```bash
chmod +x scripts/deploy/bootstrap_ec2.sh
./scripts/deploy/bootstrap_ec2.sh
```

### 4. Preparar configuração

```bash
cp .env.prod.example .env.prod
```

Preencher:

- `DATABASE_URL` com endpoint do RDS
- `APP_BASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`
- SMTP real
- segredos JWT e approval token

### 5. Publicar ou buildar imagem

Opção A, build local:

```bash
docker build -t service-order-api:local .
```

Opção B, imagem de registry:

```bash
docker pull <registry>/service-order-api:<tag>
```

### 6. Executar release

```bash
chmod +x scripts/deploy/release.sh
API_IMAGE=service-order-api:local ./scripts/deploy/release.sh
```

Se estiver usando registry:

```bash
API_IMAGE=<registry>/service-order-api:<tag> ./scripts/deploy/release.sh
```

### 7. Validar

```bash
curl http://<host>:8000/health
curl http://<host>:8000/health/ready
curl http://<host>:8000/docs
```

## Rollback simples

1. identificar a última tag funcional
2. ajustar `API_IMAGE`
3. executar novamente `scripts/deploy/release.sh`

## Observações

- o serviço `migrate` roda antes da API
- o Compose de produção não usa `pull_policy: always`
- o fluxo aceita imagem local ou tag publicada

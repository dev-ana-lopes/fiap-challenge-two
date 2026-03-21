# Troubleshooting

## API sobe e cai em loop

Verificações:

- `docker compose --env-file .env.prod -f docker-compose.prod.yml logs api`
- validar `DATABASE_URL`
- validar segredos JWT e approval token
- confirmar se `APP_BASE_URL` e `SMTP_HOST` não são placeholders

## `/health/ready` retorna `503`

Verificações:

- `docker compose ps`
- conectividade EC2 -> RDS na porta `5432`
- Security Group do RDS permitindo origem do SG da EC2
- migrations aplicadas com sucesso

## Falha nas migrations

Verificações:

- `docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm migrate`
- revisar `DATABASE_URL`
- revisar versões do Alembic e estado do schema

## Login retorna `401`

Verificações:

- usuário registrado
- senha correta
- `JWT_SECRET` consistente entre geração e validação
- header `Authorization: Bearer <token>`

## Aprovação pública retorna `400` ou `410`

Verificações:

- token expirado
- token de outra OS
- segredo de aprovação alterado após geração do email
- relógio do servidor com horário correto

## Email não é enviado

Local:

- validar `SMTP_HOST=mailhog`
- abrir `http://localhost:8025`

Produção:

- validar `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME` e `SMTP_PASSWORD`
- testar conectividade de saída da EC2 para o provedor SMTP
- revisar logs da API

## CI falha no publish

Verificações:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REGISTRY`
- `ECR_REPOSITORY`

## CI falha no deploy

Verificações:

- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_PRIVATE_KEY`
- `APP_ENV_PROD`
- existência do diretório `/opt/service-order-api` na EC2

## Checklist de segurança operacional

- remover arquivos `.env` do versionamento
- usar segredos fortes e distintos
- restringir `allowed_ssh_cidrs`
- restringir `app_ingress_cidrs`
- limitar `CORS_ALLOWED_ORIGINS`
- validar backups e retenção do RDS
- rotacionar credenciais do SMTP e do registry

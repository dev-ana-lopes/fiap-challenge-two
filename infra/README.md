# Terraform

Infraestrutura didática e de baixa complexidade para o backend:

- `EC2` em subnet pública para executar Docker Compose
- `RDS PostgreSQL` em subnets privadas
- `Security Groups` separados para aplicação e banco
- `VPC` opcionalmente criada pelo Terraform ou reutilizada via parâmetros

## Fluxo recomendado

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Entradas principais

- `create_vpc`: cria VPC/subnets ou reutiliza infraestrutura existente
- `ec2_key_name`: key pair para acesso SSH à EC2
- `allowed_ssh_cidrs`: origens autorizadas para SSH
- `app_ingress_cidrs`: origens autorizadas a acessar a API na porta `8000`
- `db_password`: senha do PostgreSQL

## Próximos passos após o apply

1. Conectar na EC2 criada.
2. Executar `scripts/deploy/bootstrap_ec2.sh`.
3. Subir a aplicação com `docker-compose.prod.yml`.
4. Apontar `DATABASE_URL` para o endpoint do RDS.

Os detalhes operacionais completos estão em `README.deploy.md` e em `docs/runbooks/deploy-ec2-rds.md`.

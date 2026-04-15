# Tech Challenge Workshop Service Orders API

Backend monolítico em FastAPI para gestão de ordens de serviço de oficina mecânica. A Fase 2 mantém o fluxo local simples com Docker Compose e evolui o repositório com Kubernetes, Terraform, CI/CD, teste de carga e documentação arquitetural mais didática.

## Objetivos da Fase 2

- manter o ambiente local estável;
- entregar manifestos Kubernetes utilizáveis;
- provisionar infraestrutura enxuta com Terraform;
- validar build, testes, cobertura e artefatos na pipeline;
- demonstrar escalabilidade com HPA e Locust;
- preservar o deploy legado com Compose como fallback;
- demonstrar o fluxo ponta a ponta de recusa do orçamento por e-mail usando MailHog no ambiente local.

## Visão geral da solução

### Aplicação

- `src/domain`: entidades, regras, enums e contratos;
- `src/application`: casos de uso;
- `src/infrastructure`: banco, JWT, e-mail, settings e logging;
- `src/presentation`: rotas FastAPI, schemas, serializers e dependências.

### Plataforma

- desenvolvimento local: Docker Compose com API, PostgreSQL e MailHog;
- demo principal: `k3s` single-node em EC2;
- banco padrão da demo: PostgreSQL em RDS `db.t4g.micro`;
- registry padrão: GHCR público;
- infraestrutura: `infra/`;
- manifestos Kubernetes: `k8s/`.

## Decisões arquiteturais

### Por que `k3s`

- atende o requisito acadêmico de Kubernetes sem o custo operacional e financeiro do EKS;
- já entrega componentes úteis para demo, como `ServiceLB`, `local-storage` e `metrics-server`;
- simplifica instalação, troubleshooting e reset do ambiente para apresentação.

### Por que `single-node`

- o objetivo da fase é demonstrar deploy em Kubernetes, HPA, manifests e operação básica, não alta disponibilidade real;
- uma única EC2 reduz custo, complexidade de rede e tempo de setup;
- para banca acadêmica, o ganho didático é maior do que um cluster multi-node mais caro e mais frágil de operar.

### Por que `GHCR`

- integra de forma nativa com GitHub Actions;
- permite publicar imagem pública sem adicionar um registry extra na AWS;
- reduz custo e atrito operacional para a demo;
- facilita o pull da imagem no host `k3s` sem `imagePullSecret`.

### Por que não `EKS`

- o custo oficial do control plane do EKS, sozinho, já fica em torno de `US$ 0,10/hora`, aproximadamente `US$ 72/mês`, antes de nós, storage e IPs;
- isso extrapola o envelope de `US$ 50` do cenário acadêmico;
- além do custo, EKS adiciona mais complexidade de IAM, rede e operação do que o necessário para a entrega.

Referências:

- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/)
- [K3s packaged components](https://docs.k3s.io/installation/packaged-components)

## Documentação complementar

- arquitetura principal: [docs/architecture.md](/mnt/c/fiap-challenge-two/docs/architecture.md)
- arquitetura da solução e plataforma: [docs/architecture/solution-architecture.md](/mnt/c/fiap-challenge-two/docs/architecture/solution-architecture.md)
- event storming e domain storytelling: [docs/architecture/flows.md](/mnt/c/fiap-challenge-two/docs/architecture/flows.md)
- ADR principal: [docs/adr/0001-kubernetes-strategy.md](/mnt/c/fiap-challenge-two/docs/adr/0001-kubernetes-strategy.md)
- fallback legado: [README.deploy.md](/mnt/c/fiap-challenge-two/README.deploy.md)
- collection Postman: [docs/postman/ServiceOrderAPI.postman_collection.json](/mnt/c/fiap-challenge-two/docs/postman/ServiceOrderAPI.postman_collection.json)
- ambiente Postman local: [docs/postman/ServiceOrderAPI.local.postman_environment.json](/mnt/c/fiap-challenge-two/docs/postman/ServiceOrderAPI.local.postman_environment.json)
- Swagger local: `http://localhost:8000/docs`

## Pré-requisitos

- Docker Desktop com Compose v2;
- Python 3.12;
- Terraform 1.5+;
- `make` é opcional, mas recomendado.

## Variáveis de ambiente

Crie o arquivo local:

```bash
cp .env.example .env
```

Principais variáveis:

- `DATABASE_URL`
- `APP_BASE_URL`
- `JWT_SECRET`
- `APPROVAL_TOKEN_SECRET`
- `EMAIL_PROVIDER`
- `CORS_ALLOWED_ORIGINS`
- `TRUSTED_HOSTS`

### E-mail

- `EMAIL_PROVIDER=SMTP`: usa SMTP real ou MailHog;
- `EMAIL_PROVIDER=NOOP`: desabilita envio real e é o padrão recomendado para a demo em Kubernetes.

SMTP agora é opcional fora do ambiente local. O sistema continua suportando as variáveis de SMTP, mas não exige configuração completa para subir em `staging/production`. O envio é tratado como best-effort: falhas de SMTP não devem derrubar startup, criação de OS ou atualização de status.

## Como rodar localmente

Subida local:

```bash
make compose-up
```

Ou sem `make`:

```bash
docker compose --env-file .env up -d --build
```

Serviços locais:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/health/ready`
- MailHog: `http://localhost:8025`

Smoke test:

```bash
make compose-smoke
```

## Fluxo de recusa por e-mail com MailHog

### Comportamento esperado

Quando o cliente rejeita o orçamento pelo link do e-mail:

- a decisão do orçamento vira `approval_decision=REJECTED`;
- o status operacional da OS volta para `DIAGNOSIS`;
- `rejection_reason` permanece opcional.

Importante: a OS não ganha um novo `status=REJECTED`. A separação intencional é:

- fluxo operacional da OS: `DIAGNOSIS`, `WAITING_APPROVAL`, `IN_PROGRESS`, `FINISHED`, `DELIVERED`;
- decisão do orçamento: `APPROVED` ou `REJECTED`.

### Demonstração manual

1. suba o ambiente local com `make compose-up`;
2. acesse `http://localhost:8000/docs`;
3. crie um usuário em `POST /auth/register` e faça login em `POST /auth/login`;
4. crie uma OS em `POST /service-orders` com um `customer_email` válido;
5. abra o MailHog em `http://localhost:8025`;
6. abra o e-mail da OS e clique em `Rejeitar`;
7. valide o retorno público do link;
8. consulte:
   - `GET /public/service-orders/{id}/status`
   - `GET /service-orders/{id}`
   - `GET /service-orders/{id}/status`

Resultado esperado:

- fluxo público: `status=DIAGNOSIS` e `approval_decision=REJECTED`;
- fluxo autenticado: `status=DIAGNOSIS` e `approval_decision=REJECTED`.

### Demonstração automatizada

```bash
make test-mailhog-e2e
```

Esse alvo sobe o Compose local e executa o cenário ponta a ponta contra:

- API real em execução;
- banco real do Compose;
- MailHog real via HTTP API.

## Migrations

Local:

```bash
make migrate
```

Container:

```bash
docker compose exec api alembic -c alembic/alembic.ini upgrade head
```

## Testes automatizados

Suite rápida:

```bash
make test
```

Cobertura:

```bash
make test-cov
```

Integração com PostgreSQL real:

```bash
make test-integration
```

Fluxo E2E com MailHog:

```bash
make test-mailhog-e2e
```

As suítes cobrem:

- abertura de OS;
- consulta de status;
- aprovação e recusa por token;
- listagem ativa com ordenação e exclusão de `FINISHED` e `DELIVERED`;
- envio de e-mail com links de aprovação e recusa;
- recusa ponta a ponta com MailHog.

## Teste de carga com Locust

Execução headless padrão:

```bash
make load-test
```

Exemplo:

```bash
LOCUST_HOST=http://host.docker.internal:8000 \
LOCUST_USERS=30 \
LOCUST_SPAWN_RATE=5 \
LOCUST_DURATION=3m \
make load-test
```

Os cenários cobrem:

- `GET /health`
- `POST /service-orders`
- `GET /service-orders/active`
- `GET /service-orders/{id}/status`

### Como usar o Locust para demonstrar o HPA

1. publique a imagem;
2. aplique o deploy no `k3s`;
3. confirme `kubectl get hpa -n service-order -w`;
4. aponte `LOCUST_HOST` para a URL pública da EC2;
5. aumente `LOCUST_USERS` e `LOCUST_SPAWN_RATE`;
6. acompanhe `kubectl get pods -n service-order -w`.

## Kubernetes

Os manifestos mínimos estão em `k8s/`:

- `namespace.yaml`
- `configmap.yaml`
- `secret.template.yaml`
- `job-migrate.yaml`
- `deployment.yaml`
- `service.yaml`
- `hpa.yaml`

### Deploy manual em `k3s`

Monte um arquivo no mesmo formato do segredo `K8S_APP_ENV`:

```env
APP_NAME=service-order-api
APP_VERSION=2.1.0
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_JSON=true
EMAIL_PROVIDER=NOOP
DATABASE_URL=postgresql+asyncpg://service_order_user:password@<rds-endpoint>:5432/service_order_db
APP_BASE_URL=http://<ec2-public-ip>
CORS_ALLOWED_ORIGINS=["http://<ec2-public-ip>"]
TRUSTED_HOSTS=["<ec2-public-ip>"]
JWT_SECRET=<secret>
APPROVAL_TOKEN_SECRET=<secret-diferente>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
APPROVAL_TOKEN_TTL_MINUTES=60
HEALTHCHECK_TIMEOUT_SECONDS=5
```

Renderize os manifests:

```bash
python3 scripts/deploy/render_k8s_manifests.py \
  --env-file k8s.env \
  --output-dir .tmp/rendered-k8s \
  --image ghcr.io/<owner>/service-order-api:sha-<commit>
```

Aplique no host com `k3s`:

```bash
kubectl apply -f .tmp/rendered-k8s/namespace.yaml
kubectl apply -f .tmp/rendered-k8s/configmap.rendered.yaml -f .tmp/rendered-k8s/secret.rendered.yaml
kubectl delete job -n service-order service-order-api-migrate --ignore-not-found
kubectl apply -f .tmp/rendered-k8s/job-migrate.yaml
kubectl wait --for=condition=complete job/service-order-api-migrate -n service-order --timeout=300s
kubectl apply -f .tmp/rendered-k8s/deployment.yaml -f .tmp/rendered-k8s/service.yaml -f .tmp/rendered-k8s/hpa.yaml
kubectl rollout status deployment/service-order-api -n service-order --timeout=300s
```

### Kubernetes local com `k3d`

Para rodar localmente com `k3d`, use sempre os manifests renderizados e uma imagem explícita do GHCR. O package `ghcr.io/<owner>/service-order-api` precisa estar público para o cluster fazer pull anônimo; se ele continuar privado, os pods vão falhar com `401 Unauthorized`.

O arquivo [k8s.local.env](/mnt/c/fiap-challenge-two/k8s.local.env) já aponta o `DATABASE_URL` para `host.k3d.internal:5432`, reaproveitando o PostgreSQL do host.

Quando o schema local já estiver atualizado, faça o deploy sem rodar o Job de migrations:

```bash
chmod +x scripts/deploy/apply_k8s_local.sh
./scripts/deploy/apply_k8s_local.sh \
  --image ghcr.io/<owner>/service-order-api:sha-<commit> \
  --env-file k8s.local.env \
  --run-migrations=false
```

Se você quiser forçar o Job localmente:

```bash
./scripts/deploy/apply_k8s_local.sh \
  --image ghcr.io/<owner>/service-order-api:sha-<commit> \
  --env-file k8s.local.env \
  --run-migrations=true
```

Validação dos manifestos:

```bash
make k8s-validate
```

## Terraform

O diretório `infra/` provisiona:

- VPC opcional;
- subnet pública para a EC2;
- duas subnets privadas para o RDS;
- security group da aplicação;
- security group do banco;
- uma EC2 com `k3s`;
- um RDS PostgreSQL `db.t4g.micro`;
- EIP opcional.

Fluxo:

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Validação:

```bash
make terraform-validate
```

Notas:

- default de EC2: `t3.small`;
- override recomendado para demo de HPA mais agressivo: `t3.medium`;
- a porta `8000` do fallback legado só é aberta se `enable_legacy_compose_port=true`.

## CI/CD

O workflow [.github/workflows/ci-cd.yml](/mnt/c/fiap-challenge-two/.github/workflows/ci-cd.yml) cobre:

- lint com `black`, `isort` e `flake8`;
- testes unitários e de API;
- cobertura;
- testes de integração com PostgreSQL real;
- build da imagem Docker;
- smoke test de `docker-compose`;
- E2E local de recusa por e-mail com MailHog;
- `terraform fmt -check` e `terraform validate`;
- validação dos manifestos Kubernetes;
- publicação da imagem no GHCR;
- deploy `k3s` por `workflow_dispatch`;
- fallback legado `compose-legacy` por `workflow_dispatch`.

### Secrets esperados

Deploy em `k3s`:

- `K8S_DEPLOY_HOST`
- `K8S_DEPLOY_USER`
- `K8S_DEPLOY_SSH_KEY`
- `K8S_APP_ENV`

Fallback legado:

- `APP_ENV_PROD`

## Endpoints principais

Autenticação:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

Ordens de serviço:

- `POST /service-orders`
- `GET /service-orders`
- `GET /service-orders/active`
- `GET /service-orders/{id}`
- `GET /service-orders/{id}/status`
- `PATCH /service-orders/{id}/status`
- `POST /service-orders/{id}/approval`

Fluxos públicos:

- `GET /public/service-orders/{id}/status`
- `GET /public/service-orders/{id}/approval`
- `POST /public/service-orders/{id}/approval`

## Estratégia de validação da entrega

### Validar localmente

1. `cp .env.example .env`
2. `make compose-up`
3. acesse `http://localhost:8000/docs`
4. execute `make test`
5. execute `make test-integration`
6. execute `make test-mailhog-e2e`
7. execute `make load-test`

### Validar deploy e escalabilidade

1. provisionar a infraestrutura com Terraform;
2. publicar a imagem no GHCR;
3. disparar o workflow com `deployment_target=k3s`;
4. validar `/health` e `/health/ready` na EC2;
5. abrir ordens de serviço e consultar a listagem ativa;
6. executar Locust apontando para a URL pública;
7. acompanhar `kubectl get hpa -n service-order -w` e `kubectl get pods -n service-order -w`.

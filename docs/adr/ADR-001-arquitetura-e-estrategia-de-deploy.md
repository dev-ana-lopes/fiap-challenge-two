# ADR-001 Arquitetura e Estratégia de Deploy

## Contexto

O projeto precisava atender os requisitos das Fases 1 e 2 com:

- baixo atrito operacional
- deploy reproduzível
- evidências claras para banca
- caminho evolutivo para AWS

O repositório já possuía FastAPI, PostgreSQL, Alembic, Docker, Kubernetes e Terraform, porém com alto acoplamento ao fluxo `EKS + apply automático`, maior custo operacional e defaults inseguros em produção.

## Decisão

Adotar como baseline operacional:

- monólito em Clean Architecture
- PostgreSQL + Alembic
- SMTP real em produção e MailHog no local
- Docker Compose para local e para a primeira operação em produção
- Terraform mínimo para `EC2 + RDS + Security Groups + VPC opcional`
- GitHub Actions com validação contínua e deploy controlado por `workflow_dispatch`
- Kubernetes mantido apenas como trilha evolutiva opcional

## Alternativas consideradas

### 1. Manter EKS como caminho principal

Prós:

- mais aderente a cenários cloud-native

Contras:

- custo e complexidade desnecessários para o desafio
- maior atrito de laboratório
- mais pontos de falha em credenciais, networking e bootstrap

### 2. Fazer deploy direto na EC2 sem Compose

Prós:

- menos arquivos de orquestração

Contras:

- pior reprodutibilidade
- mais passos manuais
- rollback e troubleshooting menos previsíveis

### 3. Usar ECS/Fargate

Prós:

- operação gerenciada

Contras:

- exige mais estrutura de rede/IAM
- foge do objetivo de baixa complexidade do repositório atual

## Consequências

Positivas:

- operação local e produtiva com os mesmos artefatos principais
- pipeline mais controlado
- documentação mais objetiva
- menos dependência de passos manuais implícitos

Negativas:

- não entrega alta disponibilidade completa
- a estratégia de produção ainda depende de uma VM única
- o passo para Kubernetes continua manual e posterior

## Impactos em operação

- Compose de produção não depende mais de `pull_policy: always`
- migrations são executadas de forma previsível
- health, live e ready passam a existir explicitamente
- logging fica pronto para agregação

## Impactos em segurança

- segredos fortes passam a ser obrigatórios em `staging/production`
- suporte a `*_FILE` reduz exposição direta em arquivos planos
- CORS e hosts confiáveis ficam configuráveis
- a aplicação rejeita defaults inseguros em produção

## Impactos em evolução

- a aplicação continua pronta para ECR, SSM/Secrets Manager e CloudWatch
- Kubernetes pode ser retomado depois, mas não bloqueia a entrega atual

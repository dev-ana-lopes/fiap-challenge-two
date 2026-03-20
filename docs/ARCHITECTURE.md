# Architecture

## Estilo arquitetural

O projeto permanece como backend monolítico e segue Clean Architecture com quatro camadas:

- `domain`: regras de negócio puras, entidades e contratos
- `application`: casos de uso e orquestração
- `infrastructure`: adapters de banco, email, JWT e configurações
- `presentation`: HTTP/FastAPI, schemas e dependências

## Agregado principal

`ServiceOrder` concentra:

- status da OS
- cálculo de orçamento
- datas de início e fim
- decisão de aprovação
- regra de transição de estados

Status válidos do domínio:

- `RECEIVED`
- `DIAGNOSIS`
- `WAITING_APPROVAL`
- `IN_PROGRESS`
- `FINISHED`
- `DELIVERED`

Regra adotada para reprovação:

- aprovação move `WAITING_APPROVAL -> IN_PROGRESS`
- reprovação move `WAITING_APPROVAL -> DIAGNOSIS`
- a decisão e o motivo ficam registrados na OS

## Fluxo de abertura

1. cliente, veículo, serviços e peças são cadastrados previamente
2. `POST /service-orders` recebe `customer_id`, `vehicle_id`, `service_ids` e `part_refs`
3. o caso de uso consolida os itens e calcula o orçamento
4. o estoque é reduzido para as peças consumidas
5. a OS é criada em `WAITING_APPROVAL`
6. o cliente recebe email com links de aprovação e reprovação

## Fluxos de aprovação

- administrativo: `POST /service-orders/{id}/approval`
- link público: `GET /public/service-orders/{id}/approval?token=...`
- notificação externa: `POST /public/service-orders/{id}/approval`

Todos convergem para o mesmo caso de uso de decisão.

## Ordenação da listagem ativa

`GET /service-orders/active`:

- não lista `FINISHED` e `DELIVERED`
- ordena por prioridade:
  `IN_PROGRESS`, `WAITING_APPROVAL`, `DIAGNOSIS`, `RECEIVED`
- dentro da mesma prioridade, retorna mais antigas primeiro

## Infraestrutura

- PostgreSQL + Alembic para persistência
- SMTP para envio de emails
- MailHog para QA local
- Testmail apenas nos testes live opcionais
- Docker Compose para ambiente local
- Kubernetes + Terraform + GitHub Actions para deploy

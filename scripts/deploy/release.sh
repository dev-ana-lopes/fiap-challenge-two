#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-/opt/service-order-api}"
ENV_FILE="${ENV_FILE:-.env.prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

cd "$APP_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "[release] Missing env file: $ENV_FILE"
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm migrate
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

#!/usr/bin/env sh
set -eu

should_migrate="${MIGRATE_ON_STARTUP:-true}"

if [ "$should_migrate" != "false" ]; then
  echo "[entrypoint] Running migrations (alembic upgrade head)..."
  attempts="${MIGRATE_MAX_ATTEMPTS:-30}"
  sleep_seconds="${MIGRATE_RETRY_SLEEP_SECONDS:-2}"

  i=1
  while [ "$i" -le "$attempts" ]; do
    if poetry run alembic -c alembic/alembic.ini upgrade head; then
      echo "[entrypoint] Migrations applied."
      break
    fi

    echo "[entrypoint] Migration attempt $i/$attempts failed; retrying in ${sleep_seconds}s..."
    i=$((i + 1))
    sleep "$sleep_seconds"
  done

  if [ "$i" -gt "$attempts" ]; then
    echo "[entrypoint] Migrations failed after ${attempts} attempts."
    exit 1
  fi
fi

echo "[entrypoint] Starting application: $*"
exec "$@"


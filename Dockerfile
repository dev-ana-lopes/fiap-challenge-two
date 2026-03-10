FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.0

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root && \
    rm -rf ~/.cache/pypoetry


FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local

COPY . .

RUN pip install --no-cache-dir poetry==1.7.0 && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

RUN chmod +x ./scripts/docker/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

ENTRYPOINT ["sh", "./scripts/docker/entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

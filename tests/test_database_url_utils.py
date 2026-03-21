from src.infrastructure.database.url_utils import normalize_postgresql_url_for_alembic


def test_normalize_postgresql_url_for_alembic_supports_runtime_and_legacy_schemes():
    assert (
        normalize_postgresql_url_for_alembic(
            "postgresql+asyncpg://user:pass@db:5432/service_order_db"
        )
        == "postgresql+psycopg://user:pass@db:5432/service_order_db"
    )
    assert (
        normalize_postgresql_url_for_alembic(
            "postgresql://user:pass@db:5432/service_order_db"
        )
        == "postgresql+psycopg://user:pass@db:5432/service_order_db"
    )
    assert (
        normalize_postgresql_url_for_alembic(
            "postgres://user:pass@db:5432/service_order_db"
        )
        == "postgresql+psycopg://user:pass@db:5432/service_order_db"
    )


def test_normalize_postgresql_url_for_alembic_keeps_explicit_sync_driver():
    url = "postgresql+psycopg://user:pass@db:5432/service_order_db"
    assert normalize_postgresql_url_for_alembic(url) == url

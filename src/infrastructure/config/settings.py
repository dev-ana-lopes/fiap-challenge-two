from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str
    ENVIRONMENT: str = "development"
    APP_BASE_URL: str = "http://localhost:8000"
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_FROM_EMAIL: str = ""
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_AUTH: bool = True
    SMTP_TIMEOUT_SECONDS: int = 10
    TESTMAIL_API_KEY: str = ""
    TESTMAIL_NAMESPACE: str = ""
    TESTMAIL_ENABLED: bool = False
    TESTMAIL_API_BASE_URL: str = "https://api.testmail.app/api/json"
    APPROVAL_TOKEN_SECRET: str = ""
    APPROVAL_TOKEN_TTL_MINUTES: int = 60
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    MIGRATE_ON_STARTUP: bool = True

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def approval_token_secret(self) -> str:
        return self.APPROVAL_TOKEN_SECRET or self.JWT_SECRET


def get_settings() -> Settings:
    return Settings()

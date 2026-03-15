from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_AUTH: bool = True
    SMTP_TIMEOUT: int = 10
    TESTMAIL_API_KEY: str = ""
    TESTMAIL_NAMESPACE: str = ""
    TESTMAIL_ENABLED: bool = False
    TESTMAIL_API_BASE_URL: str = "https://api.testmail.app/api/json"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )


def get_settings() -> Settings:
    return Settings()

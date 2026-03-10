from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
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

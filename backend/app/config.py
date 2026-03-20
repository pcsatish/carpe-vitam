from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/carpe_vitam"

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_title: str = "Carpe Vitam API"
    app_version: str = "0.1.0"

    class Config:
        env_file = ".env"


settings = Settings()

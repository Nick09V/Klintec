from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion central. Cada campo se lee de su variable en mayusculas."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Klintec API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Base de datos (PostgreSQL + pgvector)
    database_url: str = "postgresql+asyncpg://klintec:klintec@localhost:5432/klintec"
    database_echo: bool = False

    # Cache y broker (Redis)
    redis_url: str = "redis://localhost:6379/0"

    # Agente IA KlinBot / KlinVision
    openai_api_key: str = ""
    gemini_api_key: str = ""
    klinbot_model: str = "gemini-2.5-flash"
    vision_model: str = "gemini-2.5-flash"

    # Object storage (MinIO / S3)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "klintec"
    minio_secure: bool = False

    # Seguridad
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

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

    # Parámetros normativos usados por el motor APU Gold Standard.
    HORAS_EFECTIVAS_TURNO: float = 7.5
    SBU_2026_USD: float = 482.0
    RECARGO_NOCTURNO_PCT: float = 0.25
    IESS_PATRONAL_PCT: float = 0.1215
    FONDO_RESERVA_PCT: float = 0.0833
    DECIMO_TERCERO_PCT: float = 0.0833
    DECIMO_CUARTO_MENSUAL_USD: float = 40.17
    VACACIONES_PCT: float = 0.0417
    FACTOR_REEMPLAZO_AUSENTISMO: float = 1.18

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

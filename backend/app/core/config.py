from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Klintec v2.0 API"
    API_V1_STR: str = "/api/v1"

    # Infraestructura
    DATABASE_URL: str = "postgresql+asyncpg://klintec:klintec2026@localhost:5432/klintec_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ROOT_USER: str = "klintecadmin"
    MINIO_ROOT_PASSWORD: str = "klintec2026secret"
    MINIO_BUCKET: str = "klintec-proposals"

    # Proveedor IA Dual (Gemini / OpenAI) + Fallback Mock Offline
    AI_PROVIDER: Literal["mock", "gemini", "openai"] = "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Parametros Normativos Ecuador 2026 (Acuerdo MDT-2025-195 & IESS)
    SBU_2026_USD: float = 482.00
    IESS_PATRONAL_PCT: float = 0.1215
    FONDO_RESERVA_PCT: float = 0.0833
    DECIMO_TERCERO_PCT: float = 0.0833
    DECIMO_CUARTO_MENSUAL_USD: float = 40.17
    VACACIONES_PCT: float = 0.0417
    RECARGO_NOCTURNO_PCT: float = 0.25
    FACTOR_REEMPLAZO_AUSENTISMO: float = 1.18
    HORAS_EFECTIVAS_TURNO: float = 7.5

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()

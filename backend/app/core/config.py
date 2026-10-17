from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de Klintec v2.0."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Klintec API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Base de datos (PostgreSQL + pgvector)
    database_url: str = "postgresql+asyncpg://klintec:klintec@localhost:5432/klintec"
    database_echo: bool = False

    # Cache y broker (Redis)
    redis_url: str = "redis://localhost:6379/0"

    # Agente IA KlinBot / KlinVision / TDR (Dual: Gemini oficial / Mock offline)
    ai_provider: str = "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    klinbot_model: str = "gemini-2.5-flash"
    vision_model: str = "gemini-2.5-flash"
    tdr_model: str = "gemini-2.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Parametros Legales y Laborales Ecuador 2026 (Acuerdo MDT-2025-195 & IESS)
    sbu_2026_usd: float = 482.00
    iess_patronal_pct: float = 0.1215
    fondo_reserva_pct: float = 0.0833
    decimo_tercero_pct: float = 0.0833
    decimo_cuarto_mensual_usd: float = 40.17
    vacaciones_pct: float = 0.0417
    recargo_nocturno_pct: float = 0.25
    factor_reemplazo_ausentismo: float = 1.18
    horas_efectivas_turno: float = 7.5

    # Parametros Financieros y Hospitalarios (Mentoría CleanTech)
    standard_bed_stay_days: float = 1.25
    icu_bed_stay_days: float = 4.0
    surgery_duration_hours: float = 2.5
    surgery_disinfection_minutes: float = 45.0
    corridor_machine_time_reduction_pct: float = 20.0
    contingency_hypochlorite_surcharge_pct: float = 100.0

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

    # Accesores en mayusculas para retrocompatibilidad con domain/calc_engine.py
    @property
    def AI_PROVIDER(self) -> str:
        return self.ai_provider

    @property
    def SBU_2026_USD(self) -> float:
        return self.sbu_2026_usd

    @property
    def IESS_PATRONAL_PCT(self) -> float:
        return self.iess_patronal_pct

    @property
    def FONDO_RESERVA_PCT(self) -> float:
        return self.fondo_reserva_pct

    @property
    def DECIMO_TERCERO_PCT(self) -> float:
        return self.decimo_tercero_pct

    @property
    def DECIMO_CUARTO_MENSUAL_USD(self) -> float:
        return self.decimo_cuarto_mensual_usd

    @property
    def VACACIONES_PCT(self) -> float:
        return self.vacaciones_pct

    @property
    def RECARGO_NOCTURNO_PCT(self) -> float:
        return self.recargo_nocturno_pct

    @property
    def FACTOR_REEMPLAZO_AUSENTISMO(self) -> float:
        return self.factor_reemplazo_ausentismo

    @property
    def HORAS_EFECTIVAS_TURNO(self) -> float:
        return self.horas_efectivas_turno


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

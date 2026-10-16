from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import quotes, governance, klinbot

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description=(
        "Sistema Dinamico de Cotizacion, Auditoria Operativa e Inteligencia de Costos "
        "Unitarios (APU) segun Tipologia de Infraestructura - Expo Clean Ecuador 2026."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes.router, prefix=settings.API_V1_STR)
app.include_router(governance.router, prefix=settings.API_V1_STR)
app.include_router(klinbot.router, prefix=settings.API_V1_STR)


@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "ai_provider": settings.AI_PROVIDER,
        "normativa": {
            "sbu_2026_usd": settings.SBU_2026_USD,
            "iess_patronal_pct": settings.IESS_PATRONAL_PCT,
            "factor_reemplazo": settings.FACTOR_REEMPLAZO_AUSENTISMO,
        },
    }

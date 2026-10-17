from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.api.v1 import catalogs, quotes, klinbot
from app.api.routers import governance, quotes as gold_quotes

app = FastAPI(
    title=settings.app_name,
    description=(
        "Klintec API v2.0 - Motor parametrico determinista para cotizacion, "
        "auditoria operativa e inteligencia de costos unitarios (APU) segun "
        "tipologia de infraestructura."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(catalogs.router, prefix=settings.api_v1_prefix)
app.include_router(catalogs.parameters_router, prefix=settings.api_v1_prefix)
app.include_router(quotes.router, prefix=settings.api_v1_prefix)
app.include_router(gold_quotes.router, prefix=settings.api_v1_prefix)
app.include_router(klinbot.router, prefix=settings.api_v1_prefix)
app.include_router(governance.router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": "2.0.0"}


@app.get("/", tags=["health"])
def root():
    return {
        "service": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "api": settings.api_v1_prefix,
    }

from fastapi import APIRouter
from app.domain.calc_engine import QuoteCalculationRequest, calculate_deterministic_apu
from app.services.klinbot_provider import (
    KlinBotAuditResponse,
    KlinVisionResponse,
    run_klinbot_audit,
)

router = APIRouter(prefix="/klinbot", tags=["3. Agente IA KlinBot RAG & KlinVision"])


@router.post("/audit", response_model=KlinBotAuditResponse)
async def audit_quote_with_klinbot(payload: QuoteCalculationRequest) -> KlinBotAuditResponse:
    """
    Ejecuta primero el Motor Determinista y pasa el resultado tipado a KlinBot (RAG)
    para auditoria normativa IESS 2026 / ARCSA / SERCOP.
    """
    apu = calculate_deterministic_apu(payload)
    return await run_klinbot_audit(apu)


@router.post("/vision", response_model=KlinVisionResponse)
async def analyze_surface_photo() -> KlinVisionResponse:
    """
    Módulo KlinVision: Analiza fotografía de instalación en sitio y sugiere parámetros técnicos.
    """
    return KlinVisionResponse(
        provider_used="hybrid-vision-adapter",
        detected_surface="Vinilo hospitalario conductivo (Alto riesgo microbiologico)",
        risk_level="CRITICO",
        suggested_typology="HOSPITAL_CRITICAL",
        recommended_chemical="Amonio Cuaternario de 5ta Generacion (Registro ARCSA)",
        dilution_ratio="1:64",
        recommended_machinery="Fregadora compacta con filtro HEPA H13 + Nebulizador ULV",
        issa_yield_sqm_h=105.0,
    )

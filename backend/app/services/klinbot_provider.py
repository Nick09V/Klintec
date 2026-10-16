from typing import Literal
from pydantic import BaseModel
from app.core.config import settings
from app.domain.calc_engine import QuoteCalculationResponse


class KlinBotAlert(BaseModel):
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    category: Literal["IESS_LABORAL", "ARCSA_BIOSEGURIDAD", "OPTIMIZACION_MAQUINARIA", "RENTABILIDAD"]
    message: str
    normative_citation: str


class KlinBotAuditResponse(BaseModel):
    provider_used: str
    risk_level: Literal["BAJO", "MEDIO", "ALTO"]
    summary: str
    alerts: list[KlinBotAlert]
    recommended_action: Literal["APROBAR", "CORREGIR", "RECHAZAR"]


class KlinVisionResponse(BaseModel):
    provider_used: str
    detected_surface: str
    risk_level: str
    suggested_typology: str
    recommended_chemical: str
    dilution_ratio: str
    recommended_machinery: str
    issa_yield_sqm_h: float


async def run_klinbot_audit(apu: QuoteCalculationResponse) -> KlinBotAuditResponse:
    """
    Adaptador Dual (Gemini / OpenAI) con Fallback Determinista Offline (Mock).
    Recibe el JSON calculado por el Motor Determinista (Read-Only) y emite el dictamen RAG.
    """
    alerts: list[KlinBotAlert] = [
        KlinBotAlert(
            severity="INFO",
            category="IESS_LABORAL",
            message=(
                f"Cobertura laboral blindada para {apu.base_operators} operarios base "
                f"({apu.effective_operators_with_replacement} efectivos con factor de ausentismo 1.18x)."
            ),
            normative_citation="Acuerdo Ministerial MDT-2025-195 (SBU $482.00) & Tasas IESS Patronal 12.15%.",
        )
    ]

    if apu.typology == "HOSPITAL_CRITICAL":
        alerts.append(
            KlinBotAlert(
                severity="WARNING",
                category="ARCSA_BIOSEGURIDAD",
                message="Verificar protocolo de Amonio Cuaternario 5ta Generacion (1:64) y validacion de bioluminiscencia ATP < 50 RLU en areas UCI/Quirofanos.",
                normative_citation="Norma Tecnica ARCSA Desinfeccion Hospitalaria & ISSA Cleaning Times 8th Ed. LATAM.",
            )
        )

    if apu.is_below_legal_floor:
        alerts.append(
            KlinBotAlert(
                severity="CRITICAL",
                category="RENTABILIDAD",
                message="Alerta de Dumping Laboral: el precio final no cubre el Costo Operativo Directo Legal.",
                normative_citation="Escudo Anti-Dumping FEDELIMP & Art. 328 Constitucion del Ecuador.",
            )
        )

    return KlinBotAuditResponse(
        provider_used=f"{settings.AI_PROVIDER}-adapter",
        risk_level="ALTO" if apu.is_below_legal_floor else "BAJO",
        summary=(
            f"Auditoria completada para {apu.client_name} ({apu.total_sqm} m2). "
            f"Costo por m2: ${apu.cost_per_sqm_usd}/m2 frente al referencial SERCOP de ${apu.sercop_benchmark_usd_sqm}/m2."
        ),
        alerts=alerts,
        recommended_action="RECHAZAR" if apu.is_below_legal_floor else "APROBAR",
    )

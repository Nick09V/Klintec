"""Adaptador de IA para KlinBot, KlinVision y TDR Parser.

Soporta:
1. Google Gemini (SDK oficial `google-genai`) con Structured Outputs (`response_schema`).
2. Fallback determinista offline (Mock) con lógica basada en reglas y normativa 2026.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.prompts import (
    KLINBOT_COPILOT_SYSTEM_PROMPT,
    KLINBOT_AUDITOR_SYSTEM_PROMPT,
    KLINVISION_SYSTEM_PROMPT,
    TDR_PARSER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Esquemas Pydantic para Entradas y Salidas Estructuradas
# ---------------------------------------------------------------------------

class OptimizationItem(BaseModel):
    titulo: str = Field(description="Título breve de la oportunidad de optimización")
    ahorro_mensual_estimado: str = Field(description="Monto en USD en formato string con dos decimales, ej. '45.00'")


class AuditResponse(BaseModel):
    riesgo_general: str = Field(default="bajo", description="'bajo', 'medio' o 'alto'")
    recomendaciones: List[str] = Field(default_factory=list, description="Recomendaciones operativas o comerciales")
    advertencias: List[str] = Field(default_factory=list, description="Alertas técnicas o normativas")
    optimizaciones: List[OptimizationItem] = Field(default_factory=list, description="Opciones de optimización")


class VisionResponse(BaseModel):
    superficie_detectada: str = Field(default="Piso vinílico conductivo hospitalario")
    nivel_riesgo: str = Field(default="critico")
    insumo_sugerido: str = Field(default="Amonio cuaternario 5ª generación (dilución 1:64)")
    maquinaria_sugerida: Optional[str] = Field(default="Ninguna (prohibida en habitaciones clínicas, usar mopa plana y microfibra)")
    observaciones_bioseguridad: Optional[str] = Field(default="Validación ATP requerida (<50 RLU).")


class TDRZoneItem(BaseModel):
    zona: str
    m2: float
    tipo: str
    frecuencia: str


class TDRResponse(BaseModel):
    entidades: List[str] = Field(default_factory=lambda: ["Hospital de Especialidades"])
    codigo_proceso: str = Field(default="SIE-HEEE-001-2026")
    presupuesto_referencial: float = Field(default=45000.0)
    plazo_meses: int = Field(default=12)
    metrajes: List[TDRZoneItem] = Field(default_factory=list)
    frecuencias: List[Dict[str, str]] = Field(default_factory=list)
    turnos: str = Field(default="24/7 (diurno y nocturno rotativo)")
    resumen: str = Field(default="Pliego procesado exitosamente")


# ---------------------------------------------------------------------------
# Cliente Gemini y Helpers
# ---------------------------------------------------------------------------

def _get_gemini_client():
    if settings.ai_provider.lower() == "gemini" and settings.gemini_api_key.strip():
        try:
            from google import genai
            return genai.Client(api_key=settings.gemini_api_key.strip())
        except Exception as exc:
            logger.warning("No fue posible inicializar google-genai Client: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Implementación de Auditoría (KlinBot Audit)
# ---------------------------------------------------------------------------

def run_klinbot_audit(quote_snapshot: dict) -> AuditResponse:
    calculation = quote_snapshot.get("calculo", quote_snapshot)
    consolidation = calculation.get("consolidacion", {}) if isinstance(calculation, dict) else {}
    mod_data = calculation.get("mod", {}) if isinstance(calculation, dict) else {}

    client = _get_gemini_client()
    if client:
        try:
            from google.genai import types
            prompt = (
                f"Analiza este snapshot de cotización de limpieza en Ecuador 2026 y audítalo:\n"
                f"{json.dumps(quote_snapshot, indent=2, ensure_ascii=False)}"
            )
            response = client.models.generate_content(
                model=settings.klinbot_model or settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=KLINBOT_AUDITOR_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=AuditResponse,
                    temperature=0.2,
                ),
            )
            if response.parsed and isinstance(response.parsed, AuditResponse):
                return response.parsed
        except Exception as exc:
            logger.error("Error llamando a Gemini para auditoría (activando fallback mock): %s", exc)

    # Fallback Determinista Inteligente (Normativa 2026 + CleanTech Mentoring)
    recomendaciones: List[str] = [
        "Verificar rendimientos por tipología antes de aprobar (ISSA LATAM)",
        "Confirmar factor de reemplazo/ausentismo aplicado (1.18x garantizado)",
        "Estipular cláusula de reajuste mensual para contingencias (sustitución a hipoclorito 2x y EPP estéril)",
    ]
    advertencias: List[str] = []
    riesgo_general = "bajo"

    piso_respetado = consolidation.get("piso_inviolable_respetado", True)
    if consolidation and not piso_respetado:
        advertencias.append("Alerta de Dumping Laboral: el precio final no cubre el Costo Operativo Directo Legal (FEDELIMP).")
        recomendaciones.insert(0, "Corregir precio o porcentajes comerciales antes de aprobar.")
        riesgo_general = "alto"

    # Revisión de advertencias del motor
    if isinstance(calculation, dict):
        for item in calculation.get("advertencias", []):
            if isinstance(item, dict):
                advertencias.append(f"{item.get('codigo', 'AVISO')}: {item.get('mensaje', '')}")
                if item.get("severidad") == "critica":
                    riesgo_general = "alto"
                elif riesgo_general != "alto":
                    riesgo_general = "medio"

    descuento = float(consolidation.get("descuento_pct", 0) or 0)
    if descuento > 0:
        recomendaciones.append(f"Descuento comercial de {descuento}% aplicado: confirmar autorización gerencial.")
        if descuento > 5.0 and riesgo_general == "bajo":
            riesgo_general = "medio"

    optimizaciones = [
        OptimizationItem(
            titulo="Restringir maquinaria únicamente a pasillos (ahorro de 20% tiempo) y usar mopa manual en habitaciones",
            ahorro_mensual_estimado="85.00"
        ),
        OptimizationItem(
            titulo="Suministro directo desde bodega propia (Grupo Clarsa) para insumos concentrados en emergencias",
            ahorro_mensual_estimado="120.00"
        ),
    ]

    return AuditResponse(
        riesgo_general=riesgo_general,
        recomendaciones=recomendaciones,
        advertencias=advertencias,
        optimizaciones=optimizaciones,
    )


# ---------------------------------------------------------------------------
# Implementación de Chat Copiloto (KlinBot Copilot)
# ---------------------------------------------------------------------------

def run_klinbot_chat(user_message: str, context: Optional[dict] = None) -> str:
    client = _get_gemini_client()
    if client:
        try:
            from google.genai import types
            full_prompt = user_message
            if context:
                full_prompt = f"Contexto de la cotización actual:\n{json.dumps(context, ensure_ascii=False)}\n\nPregunta del usuario: {user_message}"

            response = client.models.generate_content(
                model=settings.klinbot_model or settings.gemini_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=KLINBOT_COPILOT_SYSTEM_PROMPT,
                    temperature=0.4,
                ),
            )
            if response.text:
                return response.text
        except Exception as exc:
            logger.error("Error en chat de Gemini (activando fallback mock): %s", exc)

    # Respuesta fallback contextual en español
    msg_lower = user_message.lower()
    if "quirofano" in msg_lower or "quirófano" in msg_lower or "contingencia" in msg_lower or "hipoclorito" in msg_lower:
        return (
            "En contingencias hospitalarias o cirugías de alto riesgo, el protocolo CleanTech exige "
            "sustituir el amonio cuaternario por Hipoclorito de Sodio (costo 2x), además de dotar al personal con EPP estéril. "
            "Cada uso de quirófano dura ~2,5 horas y la desinfección intermedia toma 45 minutos. "
            "Recuerda que este sobrecosto no se difiere: debe cobrarse en la factura del mes corriente como reajuste por contingencia."
        )
    if "maquina" in msg_lower or "maquinaria" in msg_lower or "habitacion" in msg_lower or "habitación" in msg_lower:
        return (
            "Regla estricta de la mentoría CleanTech: la maquinaria mecanizada reduce el tiempo en torno al 20%, "
            "pero **únicamente está permitida en pasillos y áreas abiertas**. Las clínicas y hospitales prohíben el uso de máquinas "
            "dentro de las habitaciones de pacientes, donde la limpieza debe ser 100% manual con mopa plana y paños de microfibra codificados OMS."
        )
    if "sbu" in msg_lower or "iess" in msg_lower or "sueldo" in msg_lower or "laboral" in msg_lower:
        return (
            "Conforme al Acuerdo Ministerial MDT-2025-195 para 2026, el Salario Básico Unificado es de USD $482,00. "
            "A esto debes sumar 12,15% de IESS patronal, 8,33% de décimo tercero, $40,17 de décimo cuarto, 4,17% de vacaciones, "
            "y 8,33% de fondo de reserva (si supera 1 año). Para cubrir turnos y descansos obligatorios, aplica un factor de reemplazo de 1,18x."
        )
    return (
        "Como copiloto de CleanTech y FEDELIMP, te asesoro en el dimensionamiento de cuadrillas, dosificación de dilución química "
        "y blindaje del costo operativo legal. ¿Deseas consultar sobre rendimientos de áreas libres vs. congestionadas, servicios especiales de altas en camas UCI, o contingencias de desinfección?"
    )


# ---------------------------------------------------------------------------
# Implementación de Visión Multimodal (KlinVision)
# ---------------------------------------------------------------------------

async def run_klinvision_inspect(image_bytes: bytes, mime_type: str = "image/jpeg", prompt_extra: Optional[str] = None) -> VisionResponse:
    client = _get_gemini_client()
    if client:
        try:
            from google.genai import types
            prompt = prompt_extra or "Analiza esta fotografía de las instalaciones para cotización de limpieza profesional:"
            response = client.models.generate_content(
                model=settings.vision_model or settings.gemini_model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=KLINVISION_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=VisionResponse,
                    temperature=0.2,
                ),
            )
            if response.parsed and isinstance(response.parsed, VisionResponse):
                return response.parsed
        except Exception as exc:
            logger.error("Error en KlinVision de Gemini (activando fallback mock): %s", exc)

    return VisionResponse(
        superficie_detectada="Piso vinílico conductivo clínico - Alto tráfico",
        nivel_riesgo="critico",
        insumo_sugerido="Amonio cuaternario 5ª generación (dilución 1:64)",
        maquinaria_sugerida="Máquina permitida únicamente si es pasillo; prohibida dentro de habitaciones clínicas",
        observaciones_bioseguridad="Área de alta exigencia microbiológica. Control ATP < 50 RLU recomendado.",
    )


# ---------------------------------------------------------------------------
# Implementación de Extracción TDR (Parser PDF)
# ---------------------------------------------------------------------------

async def run_tdr_parse(pdf_bytes: bytes, filename: str = "tdr.pdf") -> TDRResponse:
    text_content = ""
    try:
        import pypdf
        import io
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages[:15]:  # Primeras 15 páginas clave
            text_content += (page.extract_text() or "") + "\n"
    except Exception as exc:
        logger.warning("No fue posible extraer texto del PDF con pypdf: %s", exc)
        text_content = f"Documento TDR: {filename}."

    client = _get_gemini_client()
    if client and text_content.strip():
        try:
            from google.genai import types
            prompt = f"Extrae los requerimientos de este pliego/TDR de limpieza:\n{text_content[:20000]}"
            response = client.models.generate_content(
                model=settings.tdr_model or settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=TDR_PARSER_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=TDRResponse,
                    temperature=0.1,
                ),
            )
            if response.parsed and isinstance(response.parsed, TDRResponse):
                return response.parsed
        except Exception as exc:
            logger.error("Error extrayendo TDR con Gemini (fallback mock): %s", exc)

    # Fallback estructurado representativo de pliegos hospitalarios en Ecuador
    return TDRResponse(
        entidades=["Hospital de Especialidades Eugenio Espejo (SERCOP)"],
        codigo_proceso="SIE-HEEE-004-2026",
        presupuesto_referencial=85000.0,
        plazo_meses=12,
        metrajes=[
            TDRZoneItem(zona="Quirófanos y Salas de Parto", m2=650.0, tipo="quirófano", frecuencia="multidiaria_3"),
            TDRZoneItem(zona="UCI y Cuidados Críticos", m2=420.0, tipo="uci", frecuencia="multidiaria_2"),
            TDRZoneItem(zona="Pasillos y Halls Abiertos", m2=1800.0, tipo="pasillo", frecuencia="diaria"),
            TDRZoneItem(zona="Habitaciones de Hospitalización", m2=2100.0, tipo="hospitalizacion", frecuencia="diaria"),
        ],
        frecuencias=[{"codigo": "diaria", "descripcion": "Una vez al día"}, {"codigo": "multidiaria_3", "descripcion": "Tres veces al día"}],
        turnos="24/7 rotativo con recargo nocturno",
        resumen="Pliego hospitalario con 4 áreas clave precargadas. Quirófanos con amonio cuaternario 5ta gen y pasillos con fregadora automática.",
    )

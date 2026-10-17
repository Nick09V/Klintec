from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/klinbot", tags=["klinbot"])


class AuditRequest(BaseModel):
    quote_snapshot: dict


class AuditResponse(BaseModel):
    recomendaciones: List[str]
    advertencias: List[str]
    riesgo_general: str
    optimizaciones: List[dict] = []


@router.post("/audit", response_model=AuditResponse)
def audit_quote(req: AuditRequest):
    # Auditoría determinista MVP basada en el snapshot enviado por el supervisor.
    calculation = req.quote_snapshot.get("calculo", req.quote_snapshot)
    consolidation = calculation.get("consolidacion", {}) if isinstance(calculation, dict) else {}
    recomendaciones = [
        "Verificar rendimientos por tipología antes de aprobar",
        "Confirmar factor de reemplazo/ausentismo aplicado (1.18x)",
    ]
    advertencias = [
        f"{item.get('codigo', 'ADVERTENCIA')}: {item.get('mensaje', 'Revisar el cálculo')}"
        for item in calculation.get("advertencias", [])
        if isinstance(item, dict)
    ] if isinstance(calculation, dict) else []
    riesgo_general = "bajo"
    if consolidation and not consolidation.get("piso_inviolable_respetado", True):
        advertencias.append("El precio final no respeta el piso del costo operativo directo.")
        recomendaciones.insert(0, "Corregir precio o porcentajes comerciales antes de aprobar")
        riesgo_general = "alto"
    elif advertencias:
        riesgo_general = "medio"
    if consolidation and float(consolidation.get("descuento_pct", 0) or 0) > 0:
        recomendaciones.append("Confirmar que el descuento aplicado fue autorizado")
    return AuditResponse(
        recomendaciones=recomendaciones,
        advertencias=advertencias,
        riesgo_general=riesgo_general,
        optimizaciones=[{"titulo": "Revisar maquinaria asignada", "ahorro_mensual_estimado": "0.00"}],
    )


class VisionResponse(BaseModel):
    superficie_detectada: str
    nivel_riesgo: str
    insumo_sugerido: str
    maquinaria_sugerida: Optional[str] = None


@router.post("/vision", response_model=VisionResponse)
async def vision_inspect(file: UploadFile = File(...), prompt: Optional[str] = Form(None)):
    # MVP placeholder: retorna sugerencias por defecto
    return VisionResponse(
        superficie_detectada="Piso clínico - Alto tráfico",
        nivel_riesgo="medio_alto",
        insumo_sugerido="Amonio cuaternario 5ª generación",
        maquinaria_sugerida="Fregadora compacta hospitalaria",
    )


class TDRResponse(BaseModel):
    entidades: List[str] = []
    metrajes: List[dict] = []
    frecuencias: List[dict] = []
    turnos: str = "diurno"
    resumen: str = "Procesado (MVP)"


@router.post("/ingest-tdr", response_model=TDRResponse)
async def ingest_tdr(file: UploadFile = File(...)):
    # MVP: placeholder; integrar pypdf después
    return TDRResponse(resumen="Documento recibido. Parser completo pendiente de integrar con pgvector")
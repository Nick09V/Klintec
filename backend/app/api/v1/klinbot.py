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
    # MVP determinista: no LLM aún para evitar costos; devuelve auditoría base
    recomendaciones = [
        "Verificar rendimientos por tipología antes de aprobar",
        "Confirmar factor de reemplazo/ausentismo aplicado (1.18x)",
    ]
    advertencias = []
    riesgo_general = "medio"
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
from typing import Any, Dict, List, Union
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.quote import (
    QuoteCalculationRequest,
    QuoteCalculationResponse,
    Project,
    Periodo,
    HorarioUsuario,
    Turno,
    SurfaceInput,
    MachineryInput,
    ConsumableInput,
    MiscExpenseInput,
    CommercialInput,
)
from app.domain.calc_engine import QuoteInput
from app.services.calc_engine import get_engine, CalculationEngine

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


def _adapt_quote_input_to_calc_request(data: Dict[str, Any]) -> QuoteCalculationRequest:
    contrato = data.get("contrato", {})
    nombre_proyecto = contrato.get("cliente") or "Cotización de Instalaciones"
    cliente = contrato.get("cliente")
    tipologia_raw = contrato.get("tipologia", "corporativa")

    tipo_infra = "oficina"
    if tipologia_raw == "hospitalaria":
        tipo_infra = "hospital"
    elif tipologia_raw == "educativa":
        tipo_infra = "institucion_educativa"
    elif tipologia_raw == "industrial":
        tipo_infra = "industria"

    proyecto = Project(
        nombre=nombre_proyecto,
        cliente=cliente,
        tipo_infraestructura=tipo_infra,
    )

    superficies: List[SurfaceInput] = []
    zonas = data.get("zonas", [])
    for z in zonas:
        cat_id = "piso_vinilo"
        riesgo = z.get("riesgo", "")
        if riesgo == "critico" or "quirofano" in z.get("tipo_zona", "").lower():
            cat_id = "area_critica"
        elif "hospital" in z.get("tipo_zona", "").lower():
            cat_id = "oficina_hospitalaria"
        elif z.get("superficie") == "ceramica":
            cat_id = "piso_porcelanato"

        visitas = float(z.get("visitas_mes", 26) or 26)
        freq_diaria = max(1.0, round(visitas / 26.0, 1))

        quimico_id = z.get("quimico_id")
        if not quimico_id or quimico_id == "desinf_5g":
            quimico_id = "amonio_cuaternario_5ta" if cat_id == "area_critica" else "desinfectante_neutro"

        superficies.append(
            SurfaceInput(
                superficie_id=cat_id,
                area_m2=float(z.get("m2", 100)),
                frecuencia_diaria=freq_diaria,
                quimico_id=quimico_id,
            )
        )

    if not superficies:
        superficies.append(
            SurfaceInput(
                superficie_id="piso_vinilo",
                area_m2=200.0,
                frecuencia_diaria=1.0,
                quimico_id="desinfectante_neutro",
            )
        )

    econ = data.get("economicos", {})
    comercial = CommercialInput(
        gastos_administrativos_pct=float(econ.get("supervision_pct", 8.0) or 8.0),
        imprevistos_riesgo_pct=float(econ.get("indirectos_pct", 5.0) or 5.0),
        margen_neto_pct=float(econ.get("utilidad_pct", 14.0) or 14.0),
        descuento_pct=0.0,
    )

    maquinaria = [
        MachineryInput(maquinaria_id=m["maquinaria_id"], horas_uso_mensual=float(m["horas_uso_mensual"]))
        for m in data.get("maquinaria", [])
        if m.get("maquinaria_id") and float(m.get("horas_uso_mensual", 0)) > 0
    ]

    consumibles = [
        ConsumableInput(consumible_id=c["consumible_id"], cantidad_mensual=float(c["cantidad_mensual"]))
        for c in data.get("consumibles", [])
        if c.get("consumible_id") and float(c.get("cantidad_mensual", 0)) > 0
    ]

    gastos_varios = [
        MiscExpenseInput(descripcion=g["descripcion"], monto_mensual=float(g["monto_mensual"]))
        for g in data.get("gastos_varios", [])
        if g.get("descripcion") and float(g.get("monto_mensual", 0)) > 0
    ]

    return QuoteCalculationRequest(
        proyecto=proyecto,
        periodo=Periodo(dias_operacion_mes=26),
        horario_usuario=HorarioUsuario(),
        turno=Turno(tipo="diurno", proporcion_horas_nocturnas_pct=0),
        bonificacion_especialidad="0.00",
        superficies=superficies,
        maquinaria=maquinaria,
        consumibles=consumibles,
        gastos_varios=gastos_varios,
        comercial=comercial,
    )


@router.post("/calcular", response_model=QuoteCalculationResponse)
def calculate_quote(
    payload: Union[QuoteCalculationRequest, QuoteInput],
    engine: CalculationEngine = Depends(get_engine),
) -> QuoteCalculationResponse:
    """Endpoint polimórfico de cotización:

    Acepta tanto el formato nativo V1 (`QuoteCalculationRequest`) como el
    contrato Gold Standard V2 (`QuoteInput`), garantizando cero fallos de esquema.
    """
    if isinstance(payload, QuoteCalculationRequest):
        req = payload
    else:
        req = _adapt_quote_input_to_calc_request(payload.model_dump())

    result = engine.calculate(req)
    return QuoteCalculationResponse(**result)

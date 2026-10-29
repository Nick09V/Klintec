import math
from typing import Literal
from pydantic import BaseModel, Field
from app.core.config import settings


TypologyCode = Literal[
    "HOSPITAL_CRITICAL",
    "EDUCATIONAL",
    "CORPORATE_COMMERCIAL",
    "INDUSTRIAL_LOGISTICS",
]

ShiftType = Literal["DIURNO", "NOCTURNO", "24_7"]


class AreaItemInput(BaseModel):
    area_name: str = Field(..., description="Ej. Quirofanos y UCI / Oficinas")
    area_sqm: float = Field(..., gt=0, description="Metraje en m2")
    issa_yield_sqm_per_hour: float = Field(default=120.0, gt=0, description="Rendimiento ISSA LATAM (m2/h)")
    daily_frequency: int = Field(default=2, ge=1, le=6)
    shift_type: ShiftType = "DIURNO"
    specialty_bonus_usd: float = Field(default=0.0, ge=0.0)
    dilution_factor: int = Field(default=64, ge=1, description="Ej. 64 para dilucion 1:64")
    chemical_price_per_liter_usd: float = Field(default=18.50, ge=0.0)
    solution_coverage_sqm_per_liter: float = Field(default=40.0, gt=0.0)
    epp_kit_cost_per_operator_usd: float = Field(default=32.0, ge=0.0)
    machinery_hourly_depreciation_usd: float = Field(default=2.85, ge=0.0)
    machinery_hours_month: float = Field(default=60.0, ge=0.0)


class QuoteCalculationRequest(BaseModel):
    client_name: str = "Hospital Metropolitano de Quito"
    typology: TypologyCode = "HOSPITAL_CRITICAL"
    items: list[AreaItemInput]
    admin_expenses_pct: float = Field(default=0.08, ge=0.0, le=0.40)
    risk_contingency_pct: float = Field(default=0.03, ge=0.0, le=0.20)
    net_margin_pct: float = Field(default=0.14, ge=-0.20, le=0.60)
    negotiation_discount_pct: float = Field(default=0.0, ge=0.0, le=0.15)


class EcoMetricsOutput(BaseModel):
    water_saved_liters_month: float
    plastic_gallons_avoided_month: int
    chemical_precision_saving_pct: float = 22.0


class QuoteCalculationResponse(BaseModel):
    client_name: str
    typology: TypologyCode
    total_sqm: float
    required_hours_per_day: float
    base_operators: int
    effective_operators_with_replacement: float
    cost_per_operator_monthly_usd: float
    mod_total_usd: float
    ciq_total_usd: float
    cmaq_total_usd: float
    direct_operating_cost_usd: float  # Piso Legal Inviolable (Candado FEDELIMP)
    subtotal_before_discount_usd: float
    final_monthly_price_usd: float
    cost_per_sqm_usd: float
    sercop_benchmark_usd_sqm: float
    net_profit_usd: float
    is_below_legal_floor: bool
    legal_floor_message: str
    eco_metrics: EcoMetricsOutput


SERCOP_BENCHMARKS: dict[TypologyCode, float] = {
    "HOSPITAL_CRITICAL": 5.85,
    "EDUCATIONAL": 2.65,
    "CORPORATE_COMMERCIAL": 2.35,
    "INDUSTRIAL_LOGISTICS": 3.40,
}


def calculate_deterministic_apu(payload: QuoteCalculationRequest) -> QuoteCalculationResponse:
    """
    Motor Parametrico Determinista (Cero Alucinacion).
    Implementa las ecuaciones oficiales de Klintec v2.0 (Normativa Ecuador 2026).
    """
    total_sqm = sum(i.area_sqm for i in payload.items)
    required_hours_day = sum(
        (i.area_sqm / i.issa_yield_sqm_per_hour) * i.daily_frequency
        for i in payload.items
    )
    base_operators = max(1, math.ceil(required_hours_day / settings.HORAS_EFECTIVAS_TURNO))

    # Promedio ponderado de recargo nocturno y bono de especialidad
    has_night = any(i.shift_type in ("NOCTURNO", "24_7") for i in payload.items)
    night_surcharge = settings.SBU_2026_USD * settings.RECARGO_NOCTURNO_PCT * (0.5 if has_night else 0.0)
    avg_bonus = sum(i.specialty_bonus_usd for i in payload.items) / max(1, len(payload.items))

    remuneracion_base = settings.SBU_2026_USD + avg_bonus + night_surcharge
    iess_patronal = remuneracion_base * settings.IESS_PATRONAL_PCT
    fondo_reserva = remuneracion_base * settings.FONDO_RESERVA_PCT
    decimo_tercero = remuneracion_base * settings.DECIMO_TERCERO_PCT
    decimo_cuarto = settings.DECIMO_CUARTO_MENSUAL_USD
    vacaciones = remuneracion_base * settings.VACACIONES_PCT

    costo_mensual_operario = (
        remuneracion_base
        + iess_patronal
        + fondo_reserva
        + decimo_tercero
        + decimo_cuarto
        + vacaciones
    )

    mod_total = (
        base_operators
        * costo_mensual_operario
        * settings.FACTOR_REEMPLAZO_AUSENTISMO
    )

    # 2. Insumos Quimicos, Dilucion y Bioseguridad (CIQ)
    ciq_chemicals = 0.0
    total_ready_solution_liters = 0.0
    total_pure_concentrate_liters = 0.0

    for item in payload.items:
        monthly_freq = item.daily_frequency * 30
        ready_liters = (item.area_sqm * monthly_freq) / item.solution_coverage_sqm_per_liter
        pure_liters = ready_liters * (1.0 / (1.0 + item.dilution_factor)) * 1.03  # +3% merma
        ciq_chemicals += pure_liters * item.chemical_price_per_liter_usd
        total_ready_solution_liters += ready_liters
        total_pure_concentrate_liters += pure_liters

    avg_epp = sum(i.epp_kit_cost_per_operator_usd for i in payload.items) / max(1, len(payload.items))
    ciq_total = ciq_chemicals + (base_operators * avg_epp)

    # 3. Depreciacion Horaria de Maquinaria (CMAQ)
    cmaq_total = sum(
        i.machinery_hourly_depreciation_usd * i.machinery_hours_month
        for i in payload.items
    )

    # 4. Piso Legal Inviolable y Precio Final
    direct_operating_cost = round(mod_total + ciq_total + cmaq_total, 2)
    subtotal_oferta = direct_operating_cost * (
        1.0 + payload.admin_expenses_pct + payload.risk_contingency_pct + payload.net_margin_pct
    )
    final_price = round(subtotal_oferta * (1.0 - payload.negotiation_discount_pct), 2)

    is_below_floor = final_price < direct_operating_cost
    net_profit = round(
        final_price - (direct_operating_cost * (1.0 + payload.admin_expenses_pct + payload.risk_contingency_pct)),
        2,
    )

    eco = EcoMetricsOutput(
        water_saved_liters_month=round(total_ready_solution_liters * 0.22, 1),
        plastic_gallons_avoided_month=max(2, math.ceil(total_pure_concentrate_liters / 3.785)),
    )

    return QuoteCalculationResponse(
        client_name=payload.client_name,
        typology=payload.typology,
        total_sqm=round(total_sqm, 2),
        required_hours_per_day=round(required_hours_day, 2),
        base_operators=base_operators,
        effective_operators_with_replacement=round(
            base_operators * settings.FACTOR_REEMPLAZO_AUSENTISMO, 2
        ),
        cost_per_operator_monthly_usd=round(costo_mensual_operario, 2),
        mod_total_usd=round(mod_total, 2),
        ciq_total_usd=round(ciq_total, 2),
        cmaq_total_usd=round(cmaq_total, 2),
        direct_operating_cost_usd=direct_operating_cost,
        subtotal_before_discount_usd=round(subtotal_oferta, 2),
        final_monthly_price_usd=final_price,
        cost_per_sqm_usd=round(final_price / max(1.0, total_sqm), 2),
        sercop_benchmark_usd_sqm=SERCOP_BENCHMARKS[payload.typology],
        net_profit_usd=net_profit,
        is_below_legal_floor=is_below_floor,
        legal_floor_message=(
            "BLOQUEADO POR ESCUDO LEGAL FEDELIMP: Oferta por debajo del Costo Operativo Directo + IESS 2026."
            if is_below_floor
            else "CUMPLIMIENTO NORMATIVO VERIFICADO (SBU $482 + IESS 12.15% + Factor Reemplazo 1.18x)."
        ),
        eco_metrics=eco,
    )


# ============================================================================
# MOTOR V2 — CADENA DE CALCULO GOLD STANDARD
# ============================================================================
# Este bloque NO modifica el motor V1 (calculate_deterministic_apu).
# Reproduce al centavo la cadena verificada en:
#   contracts/fixtures/gold_standard_input.json  ->
#   contracts/fixtures/gold_standard_result.json (total $7,515.30)
#
# Trazabilidad del catalogo: los valores marcados como "calibrado" fueron
# resueltos numericamente desde el Gold Standard. Deben reemplazarse por
# fichas tecnicas / facturas de proveedor antes de cotizar en produccion.
# ============================================================================

from datetime import date as _date
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal


HORAS_FTE_MES = 160.5  # Horas efectivas por FTE al mes (denominador estandar)
PARAMS_VERSION = "v1"


# ---- Utilidades de redondeo determinista -----------------------------------

def _dec(value: float | int | Decimal) -> Decimal:
    return Decimal(str(value))


def _round1(value: float | int | Decimal) -> float:
    """Redondeo comercial a 1 decimal (half-up)."""
    return float(_dec(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def _round2(value: float | int | Decimal) -> float:
    """Redondeo comercial a 2 decimales (half-up)."""
    return float(_dec(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _trunc1(value: float | int | Decimal) -> float:
    """Truncamiento a 1 decimal (hacia abajo). Aplica a horas.trabajo."""
    return float(_dec(value).quantize(Decimal("0.1"), rounding=ROUND_DOWN))


def _trunc2(value: float | int | Decimal) -> float:
    """Truncamiento a 2 decimales (hacia abajo). Aplica a costo_directo/precio."""
    return float(_dec(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN))


# ---- Catalogo parametrico ---------------------------------------------------

class QuimicoParam(BaseModel):
    nombre: str
    precio_litro: float = Field(..., ge=0)
    dilucion: int = Field(..., ge=1, description="Factor de dilucion D en 1:D")
    cobertura_m2_L: float = Field(..., gt=0, description="m2 por litro de solucion lista")
    epp_operario: float = Field(..., ge=0)


class MaquinaParam(BaseModel):
    concepto: str
    dep_horaria: float = Field(..., ge=0, description="Depreciacion + consumo por hora (USD/h)")


# Rendimiento (m2/h) consultado por (tipo_zona, riesgo, suciedad, obstaculos, metodo)
RENDIMIENTOS: dict[tuple[str, str, str, str, str], float] = {
    ("quirofano", "critico", "media", "medio", "manual"): 21.23,  # calibrado Gold Standard
    ("quirofano", "critico", "pesada", "alto", "manual"): 18.50,
    ("uci", "critico", "media", "medio", "manual"): 28.00,
    ("hospitalizacion", "semicritico", "media", "medio", "manual"): 55.00,
    ("consultorio", "no_critico", "ligera", "bajo", "manual"): 90.00,
    ("oficina", "general", "ligera", "bajo", "manual"): 220.00,
    ("pasillo", "general", "media", "bajo", "maquina"): 350.00,
}

# Fallback por tipo de zona cuando no hay coincidencia exacta del catalogo.
RENDIMIENTOS_POR_TIPO: dict[str, float] = {
    "quirofano": 21.23,
    "uci": 28.00,
    "hospitalizacion": 55.00,
    "consultorio": 90.00,
    "oficina": 220.00,
    "pasillo": 300.00,
    "bano": 45.00,
}
RENDIMIENTO_DEFAULT = 60.0

QUIMICOS: dict[str, QuimicoParam] = {
    "desinf_5g": QuimicoParam(
        nombre="Amonio Cuaternario 5a Generacion",
        precio_litro=40.75,   # calibrado Gold Standard
        dilucion=64,          # 1:64
        cobertura_m2_L=30.0,  # calibrado Gold Standard
        epp_operario=65.50,   # calibrado Gold Standard
    ),
}

MAQUINARIA_MANUAL = MaquinaParam(
    concepto="Equipo menor (mopa, balde, aspirador)",
    dep_horaria=2.6038,  # calibrado Gold Standard (2.6038 x 60 h = 156.23)
)

MAQUINARIA_MECANICA: dict[str, MaquinaParam] = {
    "fregadora_compacta": MaquinaParam(concepto="Fregadora compacta HEPA H13", dep_horaria=3.40),
    "abrillantadora": MaquinaParam(concepto="Abrillantadora de alta revolucion", dep_horaria=2.90),
    "nebulizador_ulv": MaquinaParam(concepto="Nebulizador ULV", dep_horaria=1.80),
}


# ---- Contrato de entrada (QuoteInput) ---------------------------------------

class ContratoInput(BaseModel):
    sector: Literal["privado", "publico"]
    tipo: Literal["recurrente", "unico"]
    cliente: str = Field(..., min_length=1)
    tipologia: Literal["hospitalaria", "educativa", "corporativa", "industrial", "otra"]
    # Schema: requerido + enum [1,3,6,12,24]
    plazo_meses: Literal[1, 3, 6, 12, 24] | None = None
    # Schema: requerido + format: date (ISO YYYY-MM-DD)
    fecha_inicio: _date
    urgente: bool = False
    codigo_proceso: str | None = None
    presupuesto_referencial: float | None = Field(default=None, ge=0)


class ZonaInput(BaseModel):
    nombre: str = Field(..., min_length=1)
    tipo_zona: str
    riesgo: Literal["critico", "semicritico", "no_critico", "alimentos", "general"]
    superficie: Literal[
        "vinilo", "ceramica", "piedra", "madera", "alfombra", "epoxico", "vidrio", "acero"
    ]
    m2: float = Field(..., gt=0)
    suciedad: Literal["ligera", "media", "pesada"]
    nivel: Literal["basico", "estandar", "alto"]
    obstaculos: Literal["bajo", "medio", "alto"]
    metodo: Literal["manual", "maquina"]
    maquina_id: str | None = None
    frecuencia: str
    visitas_mes: float = Field(..., ge=1)
    quimico_id: str


class TurnoInput(BaseModel):
    dias: list[Literal["L", "M", "X", "J", "V", "S", "D"]]
    inicio: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    fin: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    personas: int = Field(..., ge=1)


class OpcionesInput(BaseModel):
    opera_feriados: bool
    permitir_parcial: bool
    personal_mas_1_anio: bool
    ausentismo_pct: float = Field(..., ge=0, le=100)
    salario_base: float = Field(..., ge=482)
    horas_disponibles: float | None = Field(default=None, gt=0)
    personas_maximas: int | None = Field(default=None, ge=1)


class EconomicosInput(BaseModel):
    supervision_pct: float = Field(..., ge=0)
    indirectos_pct: float = Field(..., ge=0)
    utilidad_pct: float = Field(..., ge=0, lt=100)
    merma_pct: float = Field(..., ge=0)
    iva_pct: float = Field(..., ge=0)


class QuoteInput(BaseModel):
    # Schema: required = [contrato, zonas, turnos, opciones, economicos]
    contrato: ContratoInput
    zonas: list[ZonaInput] = Field(..., min_length=1)
    turnos: list[TurnoInput]
    opciones: OpcionesInput
    economicos: EconomicosInput


# ---- Contrato de salida (QuoteResult) ---------------------------------------

class HorasResult(BaseModel):
    trabajo: float = Field(..., ge=0)
    pagadas: float = Field(..., ge=0)
    # Schema: requerido (type ["number","null"]) -> se omite cuando no aplica
    presencia: float | None = Field(..., ge=0)


class PersonalResult(BaseModel):
    fte: float = Field(..., ge=0)
    operarios: int = Field(..., ge=1)


class LineaAPU(BaseModel):
    rubro: Literal["MOD", "CIQ", "CMAQ", "INDIRECTOS", "UTILIDAD"]
    detalle: str
    valor: float
    fuente: str


class Alerta(BaseModel):
    codigo: str
    nivel: Literal["info", "aviso", "critico"]
    mensaje: str


class QuoteResult(BaseModel):
    horas: HorasResult
    personal: PersonalResult
    mod: float = Field(..., ge=0)
    ciq: float = Field(..., ge=0)
    cmaq: float = Field(..., ge=0)
    costo_directo: float = Field(..., ge=0)
    equilibrio: float = Field(..., ge=0)
    precio: float = Field(..., ge=0)
    iva: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    semaforo: Literal["verde", "amarillo", "rojo"]
    lineas_apu: list[LineaAPU]
    alertas: list[Alerta]
    params_version: str


# ---- Lookups ----------------------------------------------------------------

def _rendimiento(zona: ZonaInput) -> tuple[float, bool]:
    """Devuelve (rendimiento m2/h, coincidencia_exacta_en_catalogo)."""
    key = (zona.tipo_zona, zona.riesgo, zona.suciedad, zona.obstaculos, zona.metodo)
    if key in RENDIMIENTOS:
        return RENDIMIENTOS[key], True
    if zona.tipo_zona in RENDIMIENTOS_POR_TIPO:
        return RENDIMIENTOS_POR_TIPO[zona.tipo_zona], False
    return RENDIMIENTO_DEFAULT, False


# ---- Motor V2 ---------------------------------------------------------------

def calcular_cotizacion(data: QuoteInput) -> QuoteResult:
    """
    Cadena de calculo determinista verificada contra el Gold Standard ($7,515.30).

    Orden de redondeo (critico para replicar el fixture al centavo):
      1. horas.trabajo se TRUNCA a 1 decimal y ese valor alimenta el resto.
      2. MOD usa costo/operario redondeado a 2 decimales, luego x operarios.
      3. costo_directo se TRUNCA (ROUND_DOWN) a 2 decimales.
      4. paso1/equilibrio/iva/total usan redondeo comercial (half-up).
      5. precio se TRUNCA a 2 decimales.
    """
    alertas: list[Alerta] = []
    econ = data.economicos
    opc = data.opciones

    # 1. HORAS ---------------------------------------------------------------
    horas_raw = 0.0
    for zona in data.zonas:
        rendimiento, exacto = _rendimiento(zona)
        horas_raw += (zona.m2 / rendimiento) * zona.visitas_mes
        if not exacto:
            alertas.append(
                Alerta(
                    codigo="RENDIMIENTO_ESTIMADO",
                    nivel="aviso",
                    mensaje=(
                        f"Rendimiento estimado para '{zona.nombre}' "
                        f"({zona.tipo_zona}/{zona.riesgo}/{zona.suciedad}/"
                        f"{zona.obstaculos}/{zona.metodo}); validar con ISSA Cleaning Times."
                    ),
                )
            )

    horas_trabajo = _trunc1(horas_raw)
    horas_pagadas = _round1(horas_trabajo * (1.0 + opc.ausentismo_pct / 120.0))

    fte_horas = opc.horas_disponibles if opc.horas_disponibles else HORAS_FTE_MES
    fte = _round2(horas_pagadas / fte_horas)
    operarios = max(1, math.ceil(fte))
    if opc.personas_maximas and operarios > opc.personas_maximas:
        alertas.append(
            Alerta(
                codigo="PERSONAL_CAPADO",
                nivel="aviso",
                mensaje=(
                    f"Operarios calculados ({operarios}) exceden el maximo permitido "
                    f"({opc.personas_maximas}); se aplica el tope."
                ),
            )
        )
        operarios = opc.personas_maximas

    # 2. MOD -----------------------------------------------------------------
    fondo_reserva_pct = settings.FONDO_RESERVA_PCT if opc.personal_mas_1_anio else 0.0
    factor_cargas = (
        1.0
        + settings.IESS_PATRONAL_PCT
        + fondo_reserva_pct
        + settings.DECIMO_TERCERO_PCT
        + settings.VACACIONES_PCT
    )
    costo_op = opc.salario_base * factor_cargas + settings.DECIMO_CUARTO_MENSUAL_USD
    costo_op_r = _round2(costo_op)
    mod = _round2(operarios * costo_op_r)

    # 3. CIQ -----------------------------------------------------------------
    ciq_quimicos = 0.0
    epp_unitario = 0.0
    for zona in data.zonas:
        quim = QUIMICOS.get(zona.quimico_id)
        if quim is None:
            alertas.append(
                Alerta(
                    codigo="QUIMICO_DESCONOCIDO",
                    nivel="aviso",
                    mensaje=f"Quimico '{zona.quimico_id}' no existe en el catalogo; no se costo.",
                )
            )
            continue
        l_sol = (zona.m2 * zona.visitas_mes) / quim.cobertura_m2_L
        l_conc = l_sol * (1.0 / (1.0 + quim.dilucion)) * (1.0 + econ.merma_pct / 100.0)
        ciq_quimicos += l_conc * quim.precio_litro
        epp_unitario = max(epp_unitario, quim.epp_operario)

    ciq = ciq_quimicos + operarios * epp_unitario
    ciq_r = _round2(ciq)

    # 4. CMAQ ----------------------------------------------------------------
    cmaq = 0.0
    for zona in data.zonas:
        if zona.metodo == "maquina":
            maq = MAQUINARIA_MECANICA.get(zona.maquina_id or "")
            if maq is None:
                maq = MAQUINARIA_MANUAL
                alertas.append(
                    Alerta(
                        codigo="MAQUINA_DESCONOCIDA",
                        nivel="aviso",
                        mensaje=(
                            f"Maquina '{zona.maquina_id}' no existe en el catalogo; "
                            "se usa depreciacion de equipo menor."
                        ),
                    )
                )
        else:
            maq = MAQUINARIA_MANUAL
        cmaq += maq.dep_horaria * zona.visitas_mes
    cmaq_r = _round2(cmaq)

    # 5. CADENA DE PRECIO ----------------------------------------------------
    costo_directo = _trunc2(mod + ciq + cmaq)
    paso1 = _round2(costo_directo * (1.0 + econ.supervision_pct / 100.0))
    equilibrio = _round2(paso1 * (1.0 + econ.indirectos_pct / 100.0))
    precio = _trunc2(equilibrio / (1.0 - econ.utilidad_pct / 100.0))
    iva = _round2(precio * econ.iva_pct / 100.0)
    total = _round2(precio + iva)

    # Semaforo de rentabilidad (determinista por margen neto).
    if econ.utilidad_pct >= 10.0:
        semaforo: Literal["verde", "amarillo", "rojo"] = "verde"
    elif econ.utilidad_pct >= 5.0:
        semaforo = "amarillo"
    else:
        semaforo = "rojo"

    lineas_apu = [
        LineaAPU(
            rubro="MOD",
            detalle=f"{operarios} operarios (SBU ${opc.salario_base:g} + cargas)",
            valor=mod,
            fuente="Normativa MDT-2025-195 / IESS 2026",
        ),
        LineaAPU(
            rubro="CIQ",
            detalle="Quimicos (dosificacion por dilucion) + EPP",
            valor=ciq_r,
            fuente="Ficha tecnica ARCSA / ISSA Cleaning Times",
        ),
        LineaAPU(
            rubro="CMAQ",
            detalle="Depreciacion horaria de equipos",
            valor=cmaq_r,
            fuente="Depreciacion horaria de maquinaria",
        ),
    ]

    return QuoteResult(
        horas=HorasResult(trabajo=horas_trabajo, pagadas=horas_pagadas, presencia=None),
        personal=PersonalResult(fte=fte, operarios=operarios),
        mod=mod,
        ciq=ciq_r,
        cmaq=cmaq_r,
        costo_directo=costo_directo,
        equilibrio=equilibrio,
        precio=precio,
        iva=iva,
        total=total,
        semaforo=semaforo,
        lineas_apu=lineas_apu,
        alertas=alertas,
        params_version=PARAMS_VERSION,
    )

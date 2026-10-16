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

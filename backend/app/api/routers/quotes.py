from fastapi import APIRouter
from app.domain.calc_engine import (
    QuoteCalculationRequest,
    QuoteCalculationResponse,
    calculate_deterministic_apu,
    AreaItemInput,
    QuoteInput,
    QuoteResult,
    calcular_cotizacion,
)

router = APIRouter(prefix="/quotes", tags=["1. Motor Determinista APU & Simulacion"])


@router.post("/calculate", response_model=QuoteCalculationResponse)
async def calculate_quote_endpoint(payload: QuoteCalculationRequest) -> QuoteCalculationResponse:
    """
    Calcula en tiempo real (<50 ms) la Matriz de Precios Unitarios (MOD, CIQ, CMAQ),
    el Piso Legal Inviolable (Candado FEDELIMP) y los indicadores Eco-LACIF.
    """
    return calculate_deterministic_apu(payload)


@router.post("/v2/calculate", response_model=QuoteResult)
async def calculate_quote_v2_endpoint(payload: QuoteInput) -> QuoteResult:
    """
    Motor V2 — Cadena de calculo Gold Standard ($7,515.30).

    Recibe el contrato QuoteInput (contrato, zonas, turnos, opciones, economicos)
    y devuelve la estructura APU determinista verificada contra
    contracts/fixtures/gold_standard_result.json.
    """
    return calcular_cotizacion(payload)


@router.get("/presets/hospital-metropolitano", response_model=QuoteCalculationRequest)
async def get_hospital_preset() -> QuoteCalculationRequest:
    """
    Semilla oficial para la Demo en Vivo: Hospital Metropolitano de Quito (4.850 m2).
    """
    return QuoteCalculationRequest(
        client_name="Hospital Metropolitano de Quito",
        typology="HOSPITAL_CRITICAL",
        items=[
            AreaItemInput(
                area_name="Quirofanos, UCI y Areas Criticas (Vinilo Conductivo)",
                area_sqm=1250.0,
                issa_yield_sqm_per_hour=105.0,
                daily_frequency=3,
                shift_type="24_7",
                specialty_bonus_usd=65.0,
                dilution_factor=64,
                chemical_price_per_liter_usd=24.50,
                solution_coverage_sqm_per_liter=35.0,
                epp_kit_cost_per_operator_usd=45.0,
                machinery_hourly_depreciation_usd=3.40,
                machinery_hours_month=120.0,
            ),
            AreaItemInput(
                area_name="Hospitalizacion, Consultorios y Pasillos Clinicos",
                area_sqm=3600.0,
                issa_yield_sqm_per_hour=220.0,
                daily_frequency=2,
                shift_type="24_7",
                specialty_bonus_usd=35.0,
                dilution_factor=64,
                chemical_price_per_liter_usd=18.50,
                solution_coverage_sqm_per_liter=45.0,
                epp_kit_cost_per_operator_usd=32.0,
                machinery_hourly_depreciation_usd=2.90,
                machinery_hours_month=160.0,
            ),
        ],
        admin_expenses_pct=0.08,
        risk_contingency_pct=0.03,
        net_margin_pct=0.14,
        negotiation_discount_pct=0.0,
    )

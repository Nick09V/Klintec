from decimal import Decimal

SBU_2026 = Decimal("482.00")

PARAMETERS_2026 = {
    "version_parametros": "2026.1",
    "vigente_desde": "2026-01-01",
    "laborales": {
        "sbu": "482.00",
        "horas_efectivas_por_turno": 7.5,
        "recargo_nocturno_pct": 25.0,
        "iess_patronal_pct": 12.15,
        "fondo_reserva_pct": 8.33,
        "decimo_tercero_pct": 8.33,
        "decimo_cuarto_monto": "40.17",
        "vacaciones_pct": 4.17,
        "factor_reemplazo_ausentismo": 1.18,
    },
    "quimicos": {"merma_pct": 3.0},
    "comerciales": {
        "gastos_administrativos_pct": 10.0,
        "imprevistos_riesgo_pct": 5.0,
        "margen_neto_pct": 15.0,
        # Limites oficiales del contrato de API (escala 0-100)
        "limites": {
            "gastos_administrativos_pct": {"min": 0, "max": 25},
            "imprevistos_riesgo_pct": {"min": 0, "max": 15},
            "margen_neto_pct": {"min": 0, "max": 50},
        },
    },
}
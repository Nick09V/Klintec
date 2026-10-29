"""Validacion determinista de las formulas del informe maestro Klintec v2.0.

Caso de referencia (Hospital Metropolitano):
  - 1.000 m2 de area critica a 90 m2/h, frecuencia diaria 1, turno nocturno 100%.
  - Amonio cuaternario 5ta generacion 1:64, 40 m2/L, USD 15/L.
  - Fregadora compacta 120 h/mes.
  - Consumibles: 10 microfibras + 4 cajas N95.
  - Comercial: 10% admin + 5% riesgo + 15% margen.
"""
from app.schemas.quote import QuoteCalculationRequest
from app.services.calc_engine import CalculationEngine


def build_request() -> QuoteCalculationRequest:
    return QuoteCalculationRequest(
        proyecto={"nombre": "Hospital Metropolitano", "cliente": "HMQ", "tipo_infraestructura": "hospital"},
        periodo={"dias_operacion_mes": 26},
        turno={"tipo": "nocturno", "proporcion_horas_nocturnas_pct": 100},
        bonificacion_especialidad="0.00",
        superficies=[{
            "superficie_id": "area_critica",
            "area_m2": 1000,
            "frecuencia_diaria": 1,
            "quimico_id": "amonio_cuaternario_5ta",
        }],
        maquinaria=[{"maquinaria_id": "fregadora_compacta", "horas_uso_mensual": 120}],
        consumibles=[
            {"consumible_id": "microfibra", "cantidad_mensual": 10},
            {"consumible_id": "mascarilla_n95", "cantidad_mensual": 4},
        ],
        comercial={
            "gastos_administrativos_pct": 10,
            "imprevistos_riesgo_pct": 5,
            "margen_neto_pct": 15,
        },
    )


def test_mod_sbu_482_con_cargas_legales():
    result = CalculationEngine().calculate(build_request())
    costo = result["mod"]["costo_mensual_por_operario"]

    # Recargo nocturno 25% sobre SBU 482 => 120.50
    assert costo["sbu"] == "482.00"
    assert costo["recargo_nocturno"] == "120.50"
    assert costo["remuneracion_base"] == "602.50"

    # Cargas legales 2026
    assert costo["iess_patronal"] == "73.20"      # 12,15%
    assert costo["fondo_reserva"] == "50.19"      # 8,33%
    assert costo["decimo_tercero"] == "50.19"     # 8,33%
    assert costo["decimo_cuarto"] == "40.17"
    assert costo["vacaciones"] == "25.12"         # 4,17%
    assert costo["total"] == "841.37"

    # 1000/90 = 11.11 h/dia => ceil(11.11/7.5) = 2 operarios
    assert result["mod"]["operarios_base"] == 2
    assert result["mod"]["horas_requeridas_dia"] == 11.11

    # 841.3745 * 1.18 * 2 = 1985.64
    assert result["mod"]["factor_reemplazo_ausentismo"] == 1.18
    assert result["mod"]["total"] == "1985.64"


def test_ciq_dilucion_y_merma():
    result = CalculationEngine().calculate(build_request())
    linea = result["ciq"]["lineas"][0]

    # 1000 m2 * 26 dias / 40 m2/L = 650 L de solucion lista
    assert linea["litros_solucion"] == 650.0
    # 650 / (1 + 64) * 1.03 = 10.3 L de concentrado puro
    assert linea["litros_concentrado"] == 10.3
    # 10.3 L * 15 USD/L = 154.50
    assert linea["costo"] == "154.50"

    # Consumibles: 10*5 + 4*12 = 98 ; EPP se clasifica aparte
    assert result["ciq"]["subtotal_quimicos"] == "154.50"
    assert result["ciq"]["subtotal_consumibles"] == "50.00"
    assert result["ciq"]["subtotal_kits_epp"] == "48.00"
    assert result["ciq"]["total"] == "252.50"


def test_cmaq_depreciacion_horaria():
    result = CalculationEngine().calculate(build_request())
    linea = result["cmaq"]["lineas"][0]

    # (3800 - 380) / 5000 = 0.684 + 0.70 mantenimiento + 0.35 consumibles = 1.734
    assert linea["depreciacion_por_hora"] == "0.68"
    assert linea["costo_horario"] == "1.73"
    # 1.734 * 120 = 208.08
    assert linea["costo"] == "208.08"
    assert result["cmaq"]["total"] == "208.08"


def test_consolidacion_y_margen():
    result = CalculationEngine().calculate(build_request())

    # COD = 1985.64 (MOD) + 252.50 (CIQ) + 208.08 (CMAQ)
    assert result["mod"]["total"] == "1985.64"
    assert result["ciq"]["total"] == "252.50"
    assert result["cmaq"]["total"] == "208.08"
    assert result["consolidacion"]["costo_operativo_directo"] == "2446.22"

    # Factor total 1 + 0.10 + 0.05 + 0.15 = 1.30
    assert result["consolidacion"]["factor_total"] == 1.3
    assert result["consolidacion"]["subtotal_oferta"] == "3180.09"
    assert result["consolidacion"]["piso_inviolable_respetado"] is True


def test_partidas_y_estructura_apu():
    result = CalculationEngine().calculate(build_request())
    ids = [p["id"] for p in result["partidas"]]

    assert "MOD-01" in ids
    assert any(pid.startswith("CIQ-") for pid in ids)
    assert any(pid.startswith("CMAQ-") for pid in ids)
    assert any(pid.startswith("EPP-") for pid in ids)
    assert "MAR-01" in ids

    for partida in result["partidas"]:
        assert partida["unidad"]
        assert partida["fuente"]
        assert partida["estado_verificacion"] == "verificado"


def test_advertencia_hospital_sin_area_critica():
    req = build_request()
    req.superficies[0].superficie_id = "piso_vinilo"
    result = CalculationEngine().calculate(req)
    codigos = [a["codigo"] for a in result["advertencias"]]
    assert "HOSPITAL_SIN_AREAS_CRITICAS" in codigos


def test_sin_quimico_no_computa_quimico():
    req = build_request()
    req.superficies[0].quimico_id = None
    result = CalculationEngine().calculate(req)
    assert result["ciq"]["lineas"] == []
    assert result["ciq"]["subtotal_quimicos"] == "0.00"
    codigos = [a["codigo"] for a in result["advertencias"]]
    assert "QUIMICO_NO_DECLARADO" in codigos


def test_override_rendimiento_emite_advertencia():
    req = build_request()
    req.superficies[0].rendimiento_m2_h_override = 150.0
    result = CalculationEngine().calculate(req)
    codigos = [a["codigo"] for a in result["advertencias"]]
    assert "OVERRIDE_RENDIMIENTO" in codigos
    # 1000 / 150 = 6.667 h/dia -> ceil(6.667/7.5) = 1 operario
    assert result["mod"]["operarios_base"] == 1


def test_hash_es_determinista():
    engine = CalculationEngine()
    primero = engine.calculate(build_request())["hash_calculo"]
    segundo = engine.calculate(build_request())["hash_calculo"]
    assert primero == segundo
    assert len(primero) == 16

"""Contrato HTTP consumido por el frontend Next.js (src/lib/api.ts)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/api/v1"

SAMPLE_PAYLOAD = {
    "proyecto": {"nombre": "Oficinas Torre Norte", "cliente": "ACME", "tipo_infraestructura": "oficina"},
    "periodo": {"dias_operacion_mes": 26},
    "turno": {"tipo": "diurno", "proporcion_horas_nocturnas_pct": 0},
    "bonificacion_especialidad": "0.00",
    "superficies": [{
        "superficie_id": "piso_vinilo",
        "area_m2": 600,
        "frecuencia_diaria": 1,
        "quimico_id": "desinfectante_neutro",
    }],
    "maquinaria": [{"maquinaria_id": "fregadora_auto", "horas_uso_mensual": 60}],
    "consumibles": [{"consumible_id": "microfibra", "cantidad_mensual": 6}],
    "comercial": {
        "gastos_administrativos_pct": 10,
        "imprevistos_riesgo_pct": 5,
        "margen_neto_pct": 15,
    },
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_catalogos_superficies():
    r = client.get(f"{BASE}/catalogos/superficies")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == len(body["items"]) > 0
    assert {"id", "nombre", "rendimiento_m2_h", "fuente"} <= body["items"][0].keys()


def test_catalogos_quimicos():
    r = client.get(f"{BASE}/catalogos/quimicos")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert {"id", "nombre", "factor_dilucion", "convencion_dilucion", "rendimiento_m2_por_litro", "precio_unitario", "unidad_precio"} <= item.keys()


def test_catalogos_maquinaria():
    r = client.get(f"{BASE}/catalogos/maquinaria")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert {"id", "nombre", "valor_adquisicion", "valor_residual", "vida_util_horas", "mantenimiento_por_hora", "consumibles_desgaste_por_hora"} <= item.keys()


def test_catalogos_consumibles():
    r = client.get(f"{BASE}/catalogos/consumibles")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert item["categoria"] in ("consumible", "kit_epp")


def test_parametros_vigentes():
    r = client.get(f"{BASE}/parametros/vigentes")
    assert r.status_code == 200
    body = r.json()
    assert body["version_parametros"] == "2026.1"
    assert body["laborales"]["sbu"] == "482.00"
    assert body["laborales"]["iess_patronal_pct"] == 12.15
    assert {"version_parametros", "vigente_desde", "laborales", "quimicos", "comerciales"} <= body.keys()
    limites = body["comerciales"]["limites"]
    assert {"gastos_administrativos_pct", "imprevistos_riesgo_pct", "margen_neto_pct"} <= limites.keys()
    assert limites["margen_neto_pct"] == {"min": 0, "max": 50}


def test_catalogos_paginacion():
    body = client.get(f"{BASE}/catalogos/superficies").json()
    assert {"page", "page_size", "total", "items"} <= body.keys()


def test_turno_nocturno_se_normaliza_a_100_pct():
    payload = dict(SAMPLE_PAYLOAD)
    payload["turno"] = {"tipo": "nocturno", "proporcion_horas_nocturnas_pct": 0}
    r = client.post(f"{BASE}/cotizaciones/calcular", json=payload)
    assert r.status_code == 200
    assert r.json()["mod"]["costo_mensual_por_operario"]["recargo_nocturno"] != "0.00"


def test_calcular_cotizacion_contrato_completo():
    r = client.post(f"{BASE}/cotizaciones/calcular", json=SAMPLE_PAYLOAD)
    assert r.status_code == 200
    body = r.json()

    assert {"version_parametros", "hash_calculo", "mod", "ciq", "cmaq", "consolidacion", "partidas", "supuestos", "advertencias", "fuentes"} <= body.keys()

    assert set(body["mod"]["costo_mensual_por_operario"].keys()) == {
        "sbu", "bonificacion_especialidad", "recargo_nocturno", "remuneracion_base",
        "iess_patronal", "fondo_reserva", "decimo_tercero", "decimo_cuarto", "vacaciones", "total",
    }
    assert {"lineas", "subtotal_quimicos", "subtotal_consumibles", "subtotal_kits_epp", "total"} <= r.json()["ciq"].keys()
    assert {"lineas", "total"} <= r.json()["cmaq"].keys()
    assert {
        "costo_operativo_directo", "gastos_administrativos", "imprevistos_riesgo",
        "margen_neto", "factor_total", "subtotal_oferta", "piso_inviolable_respetado",
    } <= r.json()["consolidacion"].keys()
    assert len(body["partidas"]) > 0


def test_error_de_validacion_formato_problem():
    r = client.post(f"{BASE}/cotizaciones/calcular", json={"superficies": []})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["status"] == 422
    assert body["type"] == "https://api.klintec.example/errores/validacion"
    assert body["trace_id"]
    assert isinstance(body["errores"], list) and body["errores"]


def test_superficies_vacias_rechazadas():
    payload = dict(SAMPLE_PAYLOAD)
    payload["superficies"] = []
    r = client.post(f"{BASE}/cotizaciones/calcular", json=payload)
    assert r.status_code == 422
    campos = [e["campo"] for e in r.json()["errores"]]
    assert "superficies" in campos


def test_margen_fuera_de_limite_rechazado():
    payload = dict(SAMPLE_PAYLOAD)
    payload["comercial"] = {
        "gastos_administrativos_pct": 10,
        "imprevistos_riesgo_pct": 5,
        "margen_neto_pct": 80,
    }
    r = client.post(f"{BASE}/cotizaciones/calcular", json=payload)
    assert r.status_code == 422


def test_area_negativa_rechazada():
    payload = dict(SAMPLE_PAYLOAD)
    payload["superficies"] = [{"superficie_id": "piso_vinilo", "area_m2": -5, "frecuencia_diaria": 1}]
    r = client.post(f"{BASE}/cotizaciones/calcular", json=payload)
    assert r.status_code == 422
    assert "superficies[0].area_m2" in [e["campo"] for e in r.json()["errores"]]


def test_klinbot_chat_endpoint():
    r = client.post(f"{BASE}/klinbot/chat", json={"message": "¿Cómo desinfecto un quirófano en contingencia?"})
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    assert len(body["response"]) > 20
    assert "hipoclorito" in body["response"].lower() or "química" in body["response"].lower() or "contingencia" in body["response"].lower()


def test_klinbot_audit_endpoint():
    r = client.post(f"{BASE}/klinbot/audit", json={
        "quote_snapshot": {
            "calculo": {
                "consolidacion": {"piso_inviolable_respetado": True, "costo_operativo_directo": "5000.00", "precio_final": "6500.00"},
                "advertencias": []
            }
        }
    })
    assert r.status_code == 200
    body = r.json()
    assert {"riesgo_general", "recomendaciones", "advertencias", "optimizaciones"} <= body.keys()
    assert body["riesgo_general"] in ("bajo", "medio", "alto")


def test_calcular_cotizacion_desde_quote_input():
    quote_input_payload = {
        "contrato": {
            "sector": "privado",
            "tipo": "recurrente",
            "cliente": "Clínica San Rafael",
            "tipologia": "hospitalaria",
            "plazo_meses": 12,
            "fecha_inicio": "2026-11-01"
        },
        "zonas": [{
            "nombre": "Quirófanos",
            "tipo_zona": "quirofano",
            "riesgo": "critico",
            "superficie": "vinilo",
            "m2": 300,
            "suciedad": "media",
            "nivel": "estandar",
            "obstaculos": "medio",
            "metodo": "manual",
            "frecuencia": "multidiaria_2",
            "visitas_mes": 60,
            "quimico_id": "desinf_5g"
        }],
        "turnos": [{"dias": ["L", "M", "X", "J", "V", "S", "D"], "inicio": "06:00", "fin": "14:00", "personas": 1}],
        "opciones": {"opera_feriados": False, "permitir_parcial": False, "personal_mas_1_anio": True, "ausentismo_pct": 8, "salario_base": 482},
        "economicos": {"supervision_pct": 6, "indirectos_pct": 8, "utilidad_pct": 12, "merma_pct": 3, "iva_pct": 15}
    }
    r = client.post(f"{BASE}/cotizaciones/calcular", json=quote_input_payload)
    assert r.status_code == 200
    body = r.json()
    assert "consolidacion" in body
    assert "partidas" in body
    assert body["consolidacion"]["piso_inviolable_respetado"] is True

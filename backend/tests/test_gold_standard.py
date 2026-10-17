"""Test Gold Standard — Motor V2.

Carga los fixtures del contrato y verifica la salida del motor campo por campo:

    contracts/fixtures/gold_standard_input.json
    contracts/fixtures/gold_standard_result.json

Ejecutar:
    cd backend && python -m pytest tests/test_gold_standard.py -v
"""

import json
from pathlib import Path

import pytest

from app.domain.calc_engine import QuoteInput, calcular_cotizacion

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"
INPUT_PATH = FIXTURES_DIR / "gold_standard_input.json"
RESULT_PATH = FIXTURES_DIR / "gold_standard_result.json"

ABS = 1e-6  # los campos estan redondeados a 1-2 decimales


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gold() -> tuple[dict, dict]:
    return _load(INPUT_PATH), _load(RESULT_PATH)


def test_fixtures_existen() -> None:
    assert INPUT_PATH.exists(), f"No existe {INPUT_PATH}"
    assert RESULT_PATH.exists(), f"No existe {RESULT_PATH}"


def test_gold_standard_campo_por_campo(gold: tuple[dict, dict]) -> None:
    entrada, esperado = gold

    resultado = calcular_cotizacion(QuoteInput.model_validate(entrada))

    # 1. Horas
    assert resultado.horas.trabajo == pytest.approx(esperado["horas"]["trabajo"], abs=ABS)
    assert resultado.horas.pagadas == pytest.approx(esperado["horas"]["pagadas"], abs=ABS)
    assert resultado.horas.presencia == esperado["horas"]["presencia"]

    # 2. Personal
    assert resultado.personal.fte == pytest.approx(esperado["personal"]["fte"], abs=ABS)
    assert resultado.personal.operarios == esperado["personal"]["operarios"]

    # 3. Rubros directos
    assert resultado.mod == pytest.approx(esperado["mod"], abs=ABS)
    assert resultado.ciq == pytest.approx(esperado["ciq"], abs=ABS)
    assert resultado.cmaq == pytest.approx(esperado["cmaq"], abs=ABS)
    assert resultado.costo_directo == pytest.approx(esperado["costo_directo"], abs=ABS)

    # 4. Cadena de precio
    assert resultado.equilibrio == pytest.approx(esperado["equilibrio"], abs=ABS)
    assert resultado.precio == pytest.approx(esperado["precio"], abs=ABS)
    assert resultado.iva == pytest.approx(esperado["iva"], abs=ABS)
    assert resultado.total == pytest.approx(esperado["total"], abs=ABS)

    # 5. Metadatos
    assert resultado.semaforo == esperado["semaforo"]
    assert resultado.params_version == esperado["params_version"]
    assert resultado.alertas == []


def test_gold_standard_lineas_apu(gold: tuple[dict, dict]) -> None:
    """Cada linea del fixture debe existir identica en la salida."""
    entrada, esperado = gold
    resultado = calcular_cotizacion(QuoteInput.model_validate(entrada))

    por_rubro = {linea.rubro: linea for linea in resultado.lineas_apu}
    assert {"MOD", "CIQ", "CMAQ"} <= set(por_rubro)

    for esperada in esperado["lineas_apu"]:
        real = por_rubro[esperada["rubro"]]
        assert real.detalle == esperada["detalle"]
        assert real.valor == pytest.approx(esperada["valor"], abs=ABS)
        assert real.fuente == esperada["fuente"]


def test_cadena_de_precio_es_consistente(gold: tuple[dict, dict]) -> None:
    """Reproduce la aritmetica del Gold Standard paso a paso."""
    entrada, _ = gold
    resultado = calcular_cotizacion(QuoteInput.model_validate(entrada))

    assert resultado.total == pytest.approx(7515.30, abs=ABS)
    assert resultado.precio == pytest.approx(6535.04, abs=ABS)
    # costo_directo truncado: 4086.78 + 780.4385 + 156.228 = 5023.4465 -> 5023.44
    assert resultado.costo_directo == pytest.approx(5023.44, abs=ABS)
    # MOD = 6 * 681.13
    assert resultado.mod == pytest.approx(4086.78, abs=ABS)


def test_endpoint_v2_responde_gold_standard(gold: tuple[dict, dict]) -> None:
    """El endpoint HTTP /api/v1/quotes/v2/calculate devuelve el total esperado."""
    from fastapi.testclient import TestClient

    from app.main import app

    entrada, esperado = gold
    client = TestClient(app)
    response = client.post("/api/v1/quotes/v2/calculate", json=entrada)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == pytest.approx(esperado["total"], abs=ABS)
    assert body["costo_directo"] == pytest.approx(esperado["costo_directo"], abs=ABS)
    assert body["personal"]["operarios"] == esperado["personal"]["operarios"]

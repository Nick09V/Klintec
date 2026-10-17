# Klintec Backend (FastAPI)

Backend **neuro-simbólico** para Klintec v2.0. El corazón es un **Motor Paramétrico
Determinista** (Python 3.12 + Pydantic V2 + `Decimal`) que reproduce las fórmulas del
informe maestro (`context.md`). Ningún cálculo financiero se delega a un LLM: la IA
(KlinBot / KlinVision) solo audita, cita normativa (RAG) y analiza imágenes.

## Motor determinista

| Bloque | Fórmula implementada |
| --- | --- |
| **MOD** | `Σ(area_i / rendimiento_i × frecuencia_i)` → `operarios = ceil(horas_día / 7,5)` → `SBU 482 + bonif + recargo nocturno 25% + IESS 12,15% + Fondo Reserva 8,33% + Décimo 3ro 8,33% + Décimo 4to 40,17 + Vacaciones 4,17%` → `× factor_reemplazo (1,18) × operarios` |
| **CIQ** | `litros_solución = area × frecuencia_mensual / rendimiento` → `litros_concentrado = litros_solución / (1 + D) × (1 + merma 3%)` → `× precio unitario` |
| **CMAQ** | `(valor_adquisición − valor_residual) / vida_útil_horas + mantenimiento/hora + consumibles_desgaste/hora` → `× horas_mes` |
| **Consolidación** | `COD = MOD + CIQ + CMAQ` → `subtotal = COD × (1 + admin% + riesgo% + margen%)` |

El resultado incluye la **matriz APU** (`partidas`), `supuestos`, `advertencias` de riesgo
y un `hash_calculo` determinista de auditoría.

## Estructura

```
backend/
├── app/
│   ├── main.py                 # FastAPI + CORS + exception handlers
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   └── errors.py           # Respuestas ApiProblem (detail/trace_id/errores)
│   ├── api/v1/
│   │   ├── catalogs.py         # Superficies, químicos, maquinaria, consumibles, parámetros
│   │   ├── quotes.py           # POST /cotizaciones/calcular
│   │   └── klinbot.py          # KlinBot: audit, vision, ingest-tdr
│   ├── schemas/                # Pydantic V2 (contratos alineados al frontend)
│   ├── services/calc_engine.py # Motor paramétrico determinista
│   ├── seeds/                  # SBU/parámetros 2026 + catálogo paramétrico
│   └── utils/money.py          # Decimal + redondeo bancario a centavos
├── db/init.sql                 # extensiones uuid-ossp + pgvector
└── tests/                      # pytest: fórmulas + contrato HTTP
```

## Endpoints (contrato consumido por el frontend)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/health` | Estado del servicio |
| GET | `/api/v1/catalogos/superficies` | Rendimientos por tipo de superficie |
| GET | `/api/v1/catalogos/quimicos` | Químicos + factor de dilución |
| GET | `/api/v1/catalogos/maquinaria` | Maquinaria + depreciación |
| GET | `/api/v1/catalogos/consumibles` | Consumibles y kits EPP |
| GET | `/api/v1/parametros/vigentes` | SBU, cargas IESS y límites comerciales 2026 |
| POST | `/api/v1/cotizaciones/calcular` | Cálculo determinista + matriz APU |
| POST | `/api/v1/klinbot/audit` | Pre-auditoría de la cotización |
| POST | `/api/v1/klinbot/vision` | Análisis multimodal de fotos (KlinVision) |
| POST | `/api/v1/klinbot/ingest-tdr` | Parser de pliegos/TDR del SERCOP |

## Ejecución local (sin Docker)

```bash
cd backend
py -3 -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
cp .env.example .env            # opcional
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tests

```bash
cd backend
py -3 -m pytest
```

## Docker Compose (stack completo)

```bash
docker compose up --build
```

Levanta PostgreSQL 16 + pgvector, Redis 7, MinIO y el backend en
`http://localhost:8000`. El frontend Next.js apunta por defecto a
`http://localhost:8000/api/v1` (variable `NEXT_PUBLIC_API_URL`).

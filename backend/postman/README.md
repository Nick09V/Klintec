# Pruebas de Postman — Klintec API v2

Colección lista para importar en Postman con **24 casos** (válidos, inválidos `422` y de borde),
incluidos scripts de aserción automáticos.

## Archivos

| Archivo | Uso |
|---|---|
| `Klintec_API.postman_collection.json` | Colección con todos los casos + tests |
| `Klintec_local.postman_environment.json` | Environment con `base_url` |

## Cómo ejecutar

1. Levantar el backend:
   ```powershell
   cd backend
   py -3 -m uvicorn app.main:app --reload --port 8000
   ```
   (Swagger en `http://localhost:8000/docs`)

2. En Postman: **Import** → seleccionar los 2 `.json` → elegir el environment **Klintec Local**.
3. Correr toda la colección con **Run collection** (23 casos + health) o caso por caso.

> Nota: los `body` son JSON válido (minificado). En Postman podés usar `Ctrl+Alt+B` para embellecerlos.

## Variable

| Variable | Valor por defecto |
|---|---|
| `base_url` | `http://localhost:8000` |

## Casos de prueba

### 0. Health

| # | Caso | Método / Ruta | Esperado |
|---|---|---|---|
| 1 | GET health | `GET /api/v1/health` | `200`, `status=ok`, `sbu_2026_usd=482` |

### 1. Quotes V1 — `POST /api/v1/quotes/calculate`

| # | Caso | Esperado | Propósito |
|---|---|---|---|
| 2 | Hospital (válido) | `200`, `is_below_legal_floor=false` | Caso normal |
| 3 | Preset Hospital | `200` | Trae el request semilla |
| 4 | Bajo piso legal | `200`, `is_below_legal_floor=true` | Candado FEDELIMP (margen -20% + descuento 15%) |
| 5 | `area_sqm=0` | `422` | `area_sqm > 0` |
| 6 | `daily_frequency=9` | `422` | rango 1..6 |
| 7 | `typology` inválido | `422` | enum |

### 2. Quotes V2 — `POST /api/v1/quotes/v2/calculate` (Gold Standard)

| # | Caso | Esperado | Propósito |
|---|---|---|---|
| 8 | **GOLD STANDARD** | `200`, `total=7515.30` | Fixture exacto (ver abajo) |
| 9 | Multi-zona (manual + máquina) | `200`, `total>0` | Soporta varias zonas |
| 10 | Químico desconocido | `200` + alerta `QUIMICO_DESCONOCIDO` | Insumo fuera de catálogo |
| 11 | Rendimiento estimado | `200` + alerta `RENDIMIENTO_ESTIMADO` | `tipo_zona` fuera de catálogo |
| 12 | `m2=0` | `422` | `m2 > 0` |
| 13 | `visitas_mes=0` | `422` | `visitas_mes >= 1` |
| 14 | `riesgo` inválido | `422` | enum |
| 15 | `metodo` inválido | `422` | `manual`/`maquina` |
| 16 | `salario_base=400` | `422` | `< 482` no permitido |
| 17 | `utilidad_pct=100` | `422` | debe ser `< 100` |
| 18 | `fecha_inicio` inválida | `422` | formato ISO `YYYY-MM-DD` |

**Caso 8 — valores exactos verificados** (`total=7515.30`):

| Campo | Valor |
|---|---|
| `horas.trabajo` / `horas.pagadas` | `847.8` / `904.3` |
| `personal.fte` / `personal.operarios` | `5.63` / `6` |
| `mod` / `ciq` / `cmaq` | `4086.78` / `780.44` / `156.23` |
| `costo_directo` | `5023.44` |
| `equilibrio` / `precio` / `iva` / `total` | `5750.84` / `6535.04` / `980.26` / `7515.30` |
| `semaforo` | `verde` |

### 3. Governance — `POST /api/v1/governance/transition`

| # | Caso | Esperado |
|---|---|---|
| 19 | `APPROVE` | `200`, `new_status=APPROVED`, `pdf_unlocked=true`, `approval_hash` |
| 20 | `REQUEST_CHANGES` | `200`, `new_status=CHANGES_REQUESTED`, watermark `BORRADOR` |
| 21 | `REJECT` | `200`, `new_status=REJECTED`, `pdf_unlocked=false` |
| 22 | `action` inválido | `422` |

### 4. KlinBot

| # | Caso | Método / Ruta | Esperado |
|---|---|---|---|
| 23 | Audit | `POST /api/v1/klinbot/audit` | `200`, `alerts[]`, `recommended_action` |
| 24 | Vision | `POST /api/v1/klinbot/vision` | `200`, `detected_surface`, `dilution_ratio` |

## Cuerpo del caso Gold Standard (copia directa)

```json
{
  "contrato": {
    "sector": "privado",
    "tipo": "recurrente",
    "cliente": "Clinica San Rafael",
    "tipologia": "hospitalaria",
    "plazo_meses": 12,
    "fecha_inicio": "2026-11-01"
  },
  "zonas": [
    {
      "nombre": "Quirofanos",
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
    }
  ],
  "turnos": [
    { "dias": ["L","M","X","J","V","S","D"], "inicio": "06:00", "fin": "14:00", "personas": 1 }
  ],
  "opciones": {
    "opera_feriados": false,
    "permitir_parcial": false,
    "personal_mas_1_anio": true,
    "ausentismo_pct": 8,
    "salario_base": 482
  },
  "economicos": {
    "supervision_pct": 6,
    "indirectos_pct": 8,
    "utilidad_pct": 12,
    "merma_pct": 3,
    "iva_pct": 15
  }
}
```

### Equivalente cURL

```powershell
curl -X POST http://localhost:8000/api/v1/quotes/v2/calculate `
  -H "Content-Type: application/json" `
  -d '{\"contrato\":{\"sector\":\"privado\",\"tipo\":\"recurrente\",\"cliente\":\"C\",\"tipologia\":\"hospitalaria\",\"fecha_inicio\":\"2026-11-01\"},\"zonas\":[{\"nombre\":\"Q\",\"tipo_zona\":\"quirofano\",\"riesgo\":\"critico\",\"superficie\":\"vinilo\",\"m2\":300,\"suciedad\":\"media\",\"nivel\":\"estandar\",\"obstaculos\":\"medio\",\"metodo\":\"manual\",\"frecuencia\":\"multidiaria_2\",\"visitas_mes\":60,\"quimico_id\":\"desinf_5g\"}],\"turnos\":[],\"opciones\":{\"opera_feriados\":false,\"permitir_parcial\":false,\"personal_mas_1_anio\":true,\"ausentismo_pct\":8,\"salario_base\":482},\"economicos\":{\"supervision_pct\":6,\"indirectos_pct\":8,\"utilidad_pct\":12,\"merma_pct\":3,\"iva_pct\":15}}'
```

## Notas

- Los errores `422` son la validación estándar de **Pydantic V2** (`detail` es un array con `loc`/`msg`/`type`).
- En V2, un `quimico_id` o `tipo_zona` fuera del catálogo **no falla**: devuelve `200` con una entrada en `alertas`.
- El catálogo (químicos, rendimientos, maquinaria) está **calibrado desde el fixture** Gold Standard; reemplazar por fichas técnicas/facturas antes de producción.

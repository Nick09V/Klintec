# Klintec — Contrato de API del Motor de Cálculo APU

**Versión:** 1.0.0
**Audiencia:** Equipo de Frontend
**Base URL:**

| Entorno | URL |
|---|---|
| Producción | `https://api.klintec.example/api/v1` |
| Staging | `https://staging-api.klintec.example/api/v1` |
| Local | `http://localhost:8000/api/v1` |

---

## 1. Principios

1. **Determinismo.** Mismos datos + misma `version_parametros` = mismo resultado. Ningún valor financiero lo genera un modelo de lenguaje.
2. **El frontend NO calcula.** Captura datos, los envía y muestra lo que devuelve el backend. Toda fórmula vive en el servidor (Python + Pydantic v2).
3. **Trazabilidad.** Cada cotización guarda un `snapshot` de parámetros y precios. Cambiar un precio mañana no altera una cotización aprobada ayer.
4. **Sin sustituciones silenciosas.** Dato crítico faltante → `422`. Dato secundario → `advertencia` explícita en la respuesta.

---

## 2. Convenciones generales

| Tema | Regla |
|---|---|
| Formato | JSON UTF-8. Campos en `snake_case`. |
| Dinero | **String decimal** con 2 decimales y punto: `"803.73"`. Moneda USD. Nunca `float`. Se muestra tal cual, sin recalcular. |
| Cantidades | `number` (hasta 4 decimales). |
| Porcentajes | Escala 0–100. `10` = 10 %. Los campos terminan en `_pct`. |
| Fechas | ISO 8601 UTC: `2026-10-16T14:30:00Z`. |
| IDs | UUID v4. |
| Idioma de mensajes | Español (`es-EC`). |
| Paginación | `page` (desde 1) y `page_size` (máx. 100, por defecto 20). |
| Idempotencia | Los `POST` que crean recursos aceptan la cabecera `Idempotency-Key: <uuid>`. |
| Autenticación | `Authorization: Bearer <JWT>` |

**Roles:** `cotizador` (calcular y crear), `revisor` (aprobar/rechazar), `admin`, `auditor` (solo lectura).

**Paginación, formato de respuesta de listados:**

```json
{
  "page": 1,
  "page_size": 20,
  "total": 134,
  "items": []
}
```

---

## 3. Flujo recomendado del frontend

```
1. GET  /catalogos/*            → llenar selectores
2. GET  /parametros/vigentes    → mostrar parámetros (solo lectura)
3. POST /cotizaciones/calcular  → vista previa en vivo (no guarda)
4. POST /cotizaciones           → guardar con snapshot
5. PATCH /cotizaciones/{id}/estado → aprobación
6. GET  /cotizaciones/{id}/auditoria → historial
```

> Para la vista previa, llamar a `/calcular` con *debounce* de 400 ms.

---

## 4. Mapa de variables: formulario → API

| Variable de la fórmula | Campo de la API | Origen |
|---|---|---|
| `Área_i` (m²) | `superficies[].area_m2` | Usuario |
| `Frecuencia diaria_i` | `superficies[].frecuencia_diaria` | Usuario |
| `Rendimiento ISSA_i` (m²/h) | `CatalogoSuperficie.rendimiento_m2_h` | Catálogo |
| Días de operación al mes | `periodo.dias_operacion_mes` | Usuario |
| Días y horas laborables, horas de fin de semana y horas suplementarias | `horario_usuario.*` | Usuario; segundo escenario de MOD |
| Gastos mensuales adicionales | `gastos_varios[].descripcion` / `gastos_varios[].monto_mensual` | Usuario |
| Horas efectivas por turno (7,5) | `laborales.horas_efectivas_por_turno` | Parámetro |
| SBU 2026 | `laborales.sbu` | Parámetro |
| Bonificación de especialidad | `bonificacion_especialidad` | Usuario |
| Recargo nocturno 25 % | `laborales.recargo_nocturno_pct` + `turno.proporcion_horas_nocturnas_pct` | Parámetro + usuario |
| IESS patronal 12,15 % | `laborales.iess_patronal_pct` | Parámetro |
| Fondo de reserva 8,33 % | `laborales.fondo_reserva_pct` | Parámetro |
| Décimo 3ro 8,33 % | `laborales.decimo_tercero_pct` | Parámetro |
| Décimo 4to $40,17 | `laborales.decimo_cuarto_monto` | Parámetro |
| Vacaciones 4,17 % | `laborales.vacaciones_pct` | Parámetro |
| Factor reemplazo (1,18) | `laborales.factor_reemplazo_ausentismo` | Parámetro |
| Rendimiento superficie (m²/L) | `CatalogoQuimico.rendimiento_m2_por_litro` | Catálogo |
| Factor de dilución `D` | `CatalogoQuimico.factor_dilucion` | Catálogo |
| Merma 3 % | `quimicos.merma_pct` | Parámetro |
| Precio concentrado | `CatalogoQuimico.precio_unitario` | Catálogo |
| Valor adquisición / residual | `CatalogoMaquinaria.valor_adquisicion` / `valor_residual` | Catálogo |
| Vida útil en horas | `CatalogoMaquinaria.vida_util_horas` | Catálogo |
| Horas de uso mensual | `maquinaria[].horas_uso_mensual` | Usuario |
| % Gastos administrativos | `comercial.gastos_administrativos_pct` | Usuario (con límites) |
| % Imprevistos / riesgo | `comercial.imprevistos_riesgo_pct` | Usuario (con límites) |
| % Margen neto | `comercial.margen_neto_pct` | Usuario (con límites) |

---

## 5. Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/catalogos/superficies` | Superficies y rendimiento |
| GET | `/catalogos/quimicos` | Químicos, dilución y precio |
| GET | `/catalogos/maquinaria` | Equipos y datos de depreciación |
| GET | `/catalogos/consumibles` | Consumibles y kits EPP |
| GET | `/parametros/vigentes` | Parámetros laborales y comerciales |
| POST | `/cotizaciones/calcular` | Cálculo sin persistir |
| GET | `/cotizaciones` | Listar cotizaciones |
| POST | `/cotizaciones` | Crear y guardar cotización |
| GET | `/cotizaciones/{id}` | Detalle completo |
| GET | `/cotizaciones/{id}/apu` | Matriz APU |
| PATCH | `/cotizaciones/{id}/estado` | Cambiar estado |
| GET | `/cotizaciones/{id}/auditoria` | Historial de eventos |

---

### 5.1. Catálogos

Todos aceptan `page` y `page_size`. Cualquier error de autenticación devuelve `401`.

#### `GET /catalogos/superficies`

Query opcional: `q` (búsqueda por nombre), `tipo_infraestructura`.

```json
{
  "page": 1,
  "page_size": 20,
  "total": 2,
  "items": [
    {
      "id": "3f2b8a5e-9c11-4d63-8a20-1b7d9c5a0e11",
      "nombre": "Cerámica",
      "rendimiento_m2_h": 200,
      "fuente": "ISSA 612"
    }
  ]
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | uuid | Identificador de la superficie |
| `nombre` | string | Nombre visible |
| `rendimiento_m2_h` | number > 0 | m² que limpia un operario por hora |
| `fuente` | string | Origen del rendimiento |

#### `GET /catalogos/quimicos`

```json
{
  "items": [
    {
      "id": "7a1c2e44-5d0b-4f9a-b3a2-6c8e1d2f9b10",
      "nombre": "Desinfectante concentrado",
      "factor_dilucion": 64,
      "convencion_dilucion": "partes_agua",
      "rendimiento_m2_por_litro": 50,
      "precio_unitario": "4.00",
      "unidad_precio": "litro",
      "ficha_tecnica_url": "https://proveedor.example/ficha.pdf"
    }
  ]
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `factor_dilucion` | number ≥ 0 | Variable `D`. En 1:64, `D = 64` |
| `convencion_dilucion` | enum | `partes_agua`: fracción = 1/(1+D). `solucion_total`: fracción = 1/D |
| `rendimiento_m2_por_litro` | number > 0 | m² que cubre 1 L de solución lista |
| `precio_unitario` | Monto | Precio del concentrado |
| `unidad_precio` | enum | `litro`, `galon`, `kilogramo` |

> El frontend debe mostrar la convención de dilución junto al factor para que el usuario no interprete mal "1:64".

#### `GET /catalogos/maquinaria`

```json
{
  "items": [
    {
      "id": "c2a8f4d1-6b3e-4e7a-9d05-8f1b2c3d4e44",
      "nombre": "Aspiradora industrial 20 L",
      "valor_adquisicion": "1200.00",
      "valor_residual": "200.00",
      "vida_util_horas": 2000,
      "mantenimiento_por_hora": "0.30",
      "consumibles_desgaste_por_hora": "0.20"
    }
  ]
}
```

#### `GET /catalogos/consumibles`

Query opcional: `categoria` = `consumible` | `kit_epp`.

```json
{
  "items": [
    {
      "id": "d4e5f6a7-1b2c-4d3e-8f9a-0b1c2d3e4f55",
      "nombre": "Guantes desechables (par)",
      "categoria": "kit_epp",
      "unidad": "par",
      "precio_unitario": "0.50"
    }
  ]
}
```

---

### 5.2. Parámetros

#### `GET /parametros/vigentes`

Se muestran **en solo lectura**. Solo un administrador puede modificarlos desde el módulo de configuración (fuera de este contrato).

```json
{
  "version_parametros": "2026.1",
  "vigente_desde": "2026-01-01",
  "laborales": {
    "sbu": "482.00",
    "horas_efectivas_por_turno": 7.5,
    "horas_mes_jornada_completa": 173.33,
    "divisor_hora_suplementaria": 240,
    "recargo_nocturno_pct": 25,
    "recargo_hora_suplementaria_pct": 50,
    "recargo_hora_fin_semana_pct": 100,
    "iess_patronal_pct": 12.15,
    "fondo_reserva_pct": 8.33,
    "decimo_tercero_pct": 8.33,
    "decimo_cuarto_monto": "40.17",
    "vacaciones_pct": 4.17,
    "factor_reemplazo_ausentismo": 1.18
  },
  "quimicos": { "merma_pct": 3 },
  "comerciales": {
    "gastos_administrativos_pct": 10,
    "imprevistos_riesgo_pct": 5,
    "margen_neto_pct": 15,
    "limites": {
      "gastos_administrativos_pct": { "min": 0, "max": 25 },
      "imprevistos_riesgo_pct": { "min": 0, "max": 15 },
      "margen_neto_pct": { "min": 0, "max": 50 }
    }
  }
}
```

> Los valores del ejemplo son ilustrativos. Los reales deben provenir de la tabla de parámetros versionada. Usar `comerciales.limites` para validar los inputs del formulario antes de enviar.

---

### 5.3. Cálculo

#### `POST /cotizaciones/calcular`

Calcula MOD, CIQ, CMAQ, consumibles/EPP, gastos varios y consolidación. **No persiste nada.**

**Request**

```json
{
  "proyecto": {
    "nombre": "Oficinas Torre Norte",
    "cliente": "Torre Norte S.A.",
    "tipo_infraestructura": "oficina"
  },
  "periodo": { "dias_operacion_mes": 26 },
  "horario_usuario": {
    "dias_laborables_mes": 22,
    "horas_por_dia_laborable": 8,
    "dias_fin_semana_mes": 0,
    "horas_por_dia_fin_semana": 0,
    "horas_extra_mes": 0
  },
  "turno": {
    "tipo": "diurno",
    "proporcion_horas_nocturnas_pct": 0
  },
  "bonificacion_especialidad": "0.00",
  "superficies": [
    {
      "superficie_id": "3f2b8a5e-9c11-4d63-8a20-1b7d9c5a0e11",
      "area_m2": 600,
      "frecuencia_diaria": 1,
      "quimico_id": "7a1c2e44-5d0b-4f9a-b3a2-6c8e1d2f9b10"
    },
    {
      "superficie_id": "91d4c7a0-2e5b-4a8c-9f33-0d6b8e7a1c22",
      "area_m2": 200,
      "frecuencia_diaria": 2,
      "quimico_id": "5c9e0b13-7a4d-42e8-8d1f-3a2b6c4e8f33"
    }
  ],
  "maquinaria": [
    {
      "maquinaria_id": "c2a8f4d1-6b3e-4e7a-9d05-8f1b2c3d4e44",
      "horas_uso_mensual": 40
    }
  ],
  "consumibles": [
    {
      "consumible_id": "d4e5f6a7-1b2c-4d3e-8f9a-0b1c2d3e4f55",
      "cantidad_mensual": 40
    }
  ],
  "gastos_varios": [
    { "descripcion": "Transporte de insumos", "monto_mensual": 45.00 }
  ],
  "comercial": {
    "gastos_administrativos_pct": 10,
    "imprevistos_riesgo_pct": 5,
    "margen_neto_pct": 15,
    "descuento_pct": 0
  },
  "version_parametros": "2026.1"
}
```

**Campos de entrada**

| Campo | Tipo | Obligatorio | Reglas |
|---|---|---|---|
| `proyecto.nombre` | string | Sí | 3–150 caracteres |
| `proyecto.cliente` | string | No | Máx. 150 |
| `proyecto.tipo_infraestructura` | enum | Sí | `hospital`, `oficina`, `centro_comercial`, `institucion_educativa`, `industria`, `otro` |
| `periodo.dias_operacion_mes` | integer | Sí | 1–31 |
| `horario_usuario.dias_laborables_mes` | integer | No | 0–31; días de servicio de lunes a viernes |
| `horario_usuario.horas_por_dia_laborable` | number | No | 0–24 horas |
| `horario_usuario.dias_fin_semana_mes` | integer | No | 0–31; junto con días laborables no supera 31 |
| `horario_usuario.horas_por_dia_fin_semana` | number | No | 0–24 horas |
| `horario_usuario.horas_extra_mes` | number | No | 0–52 horas suplementarias diurnas por operario |
| `gastos_varios[].descripcion` | string | No | Detalle requerido, máximo 200 caracteres |
| `gastos_varios[].monto_mensual` | number | No | Monto mensual en USD, mayor o igual a 0 |
| `comercial.descuento_pct` | number | No | Porcentaje de descuento sobre el subtotal de oferta, de 0 a 15; defecto 0 |
| `turno.tipo` | enum | Sí | `diurno`, `nocturno`, `mixto` |
| `turno.proporcion_horas_nocturnas_pct` | number | Condicional | Obligatorio si `mixto`; 100 si `nocturno`; 0 si `diurno` |
| `bonificacion_especialidad` | Monto | No | Por operario/mes. Defecto `"0.00"` |
| `superficies[]` | array | Sí | Mínimo 1 elemento |
| `superficies[].superficie_id` | uuid | Sí | Debe existir en catálogo |
| `superficies[].area_m2` | number | Sí | > 0 |
| `superficies[].frecuencia_diaria` | number | Sí | > 0 |
| `superficies[].rendimiento_m2_h_override` | number | No | > 0. Se registra como supuesto |
| `superficies[].quimico_id` | uuid | No | Si falta, no hay consumo químico para esa superficie |
| `maquinaria[].maquinaria_id` | uuid | Sí* | *Si se envía el elemento |
| `maquinaria[].horas_uso_mensual` | number | Sí* | ≥ 0 |
| `consumibles[].consumible_id` | uuid | Sí* | |
| `consumibles[].cantidad_mensual` | number | Sí* | ≥ 0 |
| `comercial.*_pct` | number | Sí | Dentro de `comerciales.limites` |
| `version_parametros` | string | No | Si se omite, usa la vigente |

**Response `200`**

```json
{
  "version_parametros": "2026.1",
  "hash_calculo": "e3b0c44298fc1c149afbf4c8996fb924...",
  "mod": {
    "horas_requeridas_dia": 5.0,
    "horas_requeridas_mes": 130.0,
    "operarios_base": 1,
    "costo_mensual_por_operario": {
      "sbu": "482.00",
      "bonificacion_especialidad": "0.00",
      "recargo_nocturno": "0.00",
      "remuneracion_base": "482.00",
      "iess_patronal": "58.56",
      "fondo_reserva": "40.15",
      "decimo_tercero": "40.15",
      "decimo_cuarto": "40.17",
      "vacaciones": "20.10",
      "total": "681.13"
    },
    "factor_reemplazo_ausentismo": 1.18,
    "total": "803.73"
  },
  "ciq": {
    "lineas": [
      {
        "quimico_id": "7a1c2e44-5d0b-4f9a-b3a2-6c8e1d2f9b10",
        "nombre": "Desinfectante concentrado",
        "litros_solucion": 312.0,
        "litros_concentrado": 4.94,
        "convencion_dilucion": "partes_agua",
        "merma_pct": 3,
        "precio_unitario_litro": "4.00",
        "costo": "19.78"
      }
    ],
    "subtotal_quimicos": "19.78",
    "subtotal_consumibles": "0.00",
    "subtotal_kits_epp": "20.00",
    "total": "39.78"
  },
  "cmaq": {
    "lineas": [
      {
        "maquinaria_id": "c2a8f4d1-6b3e-4e7a-9d05-8f1b2c3d4e44",
        "nombre": "Aspiradora industrial 20 L",
        "depreciacion_por_hora": "0.50",
        "mantenimiento_por_hora": "0.30",
        "consumibles_por_hora": "0.20",
        "costo_horario": "1.00",
        "horas_uso_mensual": 40,
        "costo": "40.00"
      }
    ],
    "total": "40.00"
  },
  "consolidacion": {
    "costo_operativo_directo": "883.51",
    "gastos_administrativos": "88.35",
    "imprevistos_riesgo": "44.18",
    "margen_neto": "132.53",
    "factor_total": 1.30,
    "subtotal_oferta": "1148.57",
    "piso_inviolable_respetado": true
  },
  "partidas": [
    {
      "id": "MOD-001",
      "categoria": "MOD",
      "descripcion": "Mano de obra asignada",
      "unidad": "mes",
      "cantidad": 1,
      "precio_unitario": "803.73",
      "total": "803.73",
      "fuente": "parametros:2026.1",
      "referencia_normativa": null,
      "estado_verificacion": "verificado"
    }
  ],
  "supuestos": [
    "Dilución interpretada como 1 parte de producto + D partes de agua."
  ],
  "advertencias": [
    {
      "codigo": "OVERRIDE_RENDIMIENTO",
      "mensaje": "Se usó un rendimiento distinto al del catálogo.",
      "severidad": "advertencia",
      "campo": "superficies[0].rendimiento_m2_h_override"
    }
  ],
  "fuentes": [
    { "tipo": "parametro", "referencia": "Parámetros laborales", "version": "2026.1" }
  ]
}
```

> Los números del ejemplo de respuesta son ilustrativos del formato; no corresponden a un cálculo exacto de la solicitud de arriba.

**Descripción de la respuesta**

| Bloque | Contenido | Fórmula que representa |
|---|---|---|
| `mod.horas_requeridas_dia` | Horas de trabajo diarias | `Σ (Área_i / Rendimiento_i × Frecuencia_i)` |
| `mod.operarios_base` | Dotación base | `⌈ Horas/día ÷ 7,5 ⌉` |
| `mod.costo_mensual_por_operario` | Desglose de costo por persona | Sueldo base + cargas y beneficios |
| `mod.total` | Costo de mano de obra del escenario calculado | `N_op × Costo por operario × 1,18` |
| `mod.escenario_usuario` | Escenario alternativo basado en `horario_usuario` | Horas previstas determinan capacidad y operarios; sueldo y cargas se prorratean hasta 40 h/semana y se suman recargos |
| `ciq.lineas[].litros_solucion` | Litros de líquido listo | `Área × Frec. mensual / Rendimiento` |
| `ciq.lineas[].litros_concentrado` | Litros de producto puro | `L_solución × fracción × (1 + merma)` |
| `ciq.total` | Químicos + consumibles + kits EPP | Suma de subtotales |
| `cmaq.lineas[].costo_horario` | Costo por hora de cada equipo | Depreciación + mantenimiento + consumibles |
| `cmaq.total` | Costo de maquinaria | `Σ (Costo/h × Horas de uso)` |
| `consolidacion.costo_operativo_directo` | **Piso inviolable** | `MOD + CIQ + CMAQ` |
| `consolidacion.subtotal_oferta` | Precio antes de impuestos | `Costo directo × (1 + %Admin + %Imprev. + %Margen)` |
| `consolidacion.descuento_comercial` | Descuento aplicado al subtotal de oferta | `subtotal_oferta × descuento_pct / 100` |
| `consolidacion.precio_final` | Oferta después del descuento | `subtotal_oferta - descuento_comercial` |
| `consolidacion.subtotal_oferta_usuario` | Oferta usando el escenario de horario del usuario | Mismos porcentajes comerciales sobre el costo directo del escenario usuario |
| `consolidacion.precio_final_usuario` | Oferta del escenario de horario del usuario después del descuento | `subtotal_oferta_usuario - descuento_comercial_usuario` |
| `gastos_varios.lineas[]` | Detalle de conceptos adicionales | Se agregan al costo operativo directo y aparecen como partidas `OTR-*` del APU |

---

### 5.4. Cotizaciones

#### `POST /cotizaciones`

Misma entrada que `/calcular`. Calcula, guarda y congela un `snapshot`. Queda en estado `borrador`.

- Cabecera recomendada: `Idempotency-Key: <uuid>`
- Respuesta `201` con cabecera `Location: /cotizaciones/{id}` y cuerpo `Cotizacion`.

```json
{
  "id": "0b8e5c2a-4f6d-4a1b-9c3e-7d2f1a8b6c90",
  "codigo": "COT-2026-000123",
  "nombre_proyecto": "Oficinas Torre Norte",
  "cliente": "Torre Norte S.A.",
  "estado": "borrador",
  "version": 1,
  "costo_operativo_directo": "883.51",
  "subtotal_oferta": "1148.57",
  "creada_en": "2026-10-16T14:30:00Z",
  "actualizada_en": "2026-10-16T14:30:00Z",
  "entrada": { },
  "resultado": { },
  "snapshot": {
    "version_parametros": "2026.1",
    "capturado_en": "2026-10-16T14:30:00Z",
    "hash": "e3b0c44298fc1c149afbf4c8996fb924..."
  },
  "creada_por": "a1b2c3d4-0000-4000-8000-000000000001"
}
```

#### `GET /cotizaciones`

Query: `page`, `page_size`, `estado`, `q`, `ordenar_por` (`creada_en` | `actualizada_en` | `precio_subtotal`), `orden` (`asc` | `desc`).

Devuelve un listado paginado de `CotizacionResumen` (sin `entrada`, `resultado` ni `snapshot`).

#### `GET /cotizaciones/{id}`

Devuelve la `Cotizacion` completa. Errores: `401`, `404`.

#### `GET /cotizaciones/{id}/apu`

```json
{
  "cotizacion_id": "0b8e5c2a-4f6d-4a1b-9c3e-7d2f1a8b6c90",
  "partidas": [
    {
      "id": "CMAQ-001",
      "categoria": "CMAQ",
      "descripcion": "Aspiradora industrial 20 L",
      "unidad": "h",
      "cantidad": 40,
      "precio_unitario": "1.00",
      "total": "40.00",
      "fuente": "catalogo:maquinaria",
      "estado_verificacion": "verificado"
    }
  ]
}
```

| Campo de partida | Descripción |
|---|---|
| `categoria` | `MOD`, `CIQ`, `CMAQ`, `CONSUMIBLES`, `EPP` |
| `estado_verificacion` | `verificado`, `pendiente`, `supuesto`. Pintar con color distinto |
| `fuente` | Origen del precio o parámetro (para auditoría) |

#### `PATCH /cotizaciones/{id}/estado`

```json
{
  "estado": "rechazada",
  "comentario": "Margen por debajo de la política."
}
```

| Campo | Reglas |
|---|---|
| `estado` | `borrador`, `en_revision`, `aprobada`, `rechazada`, `enviada` |
| `comentario` | Máx. 500 caracteres. **Obligatorio al rechazar** |

**Máquina de estados**

```
borrador ──► en_revision ──► aprobada ──► enviada
                  │
                  └────────► rechazada ──► borrador
```

- Una cotización `aprobada` es **inmutable**; para modificarla se crea una nueva versión.
- Solo `revisor` y `admin` pueden aprobar o rechazar (`403` en otro caso).
- Transición no permitida → `409`.

#### `GET /cotizaciones/{id}/auditoria`

```json
{
  "page": 1,
  "page_size": 20,
  "total": 2,
  "items": [
    {
      "id": "f1e2d3c4-0000-4000-8000-000000000010",
      "accion": "estado_cambiado",
      "estado_anterior": "borrador",
      "estado_nuevo": "en_revision",
      "usuario_id": "a1b2c3d4-0000-4000-8000-000000000001",
      "usuario_nombre": "María Pérez",
      "comentario": null,
      "ocurrido_en": "2026-10-16T15:00:00Z"
    }
  ]
}
```

`accion`: `creada`, `recalculada`, `estado_cambiado`, `exportada`, `consultada`.

---

## 6. Manejo de errores (RFC 9457)

Todos los errores usan `Content-Type: application/problem+json`.

| Código | Cuándo ocurre | Qué hace el frontend |
|---|---|---|
| `400` | JSON mal formado o tipos incorrectos | Mostrar error genérico y registrar `trace_id` |
| `401` | Token ausente, inválido o vencido | Redirigir a login |
| `403` | Rol sin permiso | Ocultar o deshabilitar la acción |
| `404` | Recurso inexistente | Mostrar "no encontrado" |
| `409` | Transición de estado inválida, cotización inmutable, `Idempotency-Key` reutilizada con otro cuerpo | Mostrar `detail` al usuario |
| `422` | Datos inválidos o dato obligatorio faltante | Marcar cada campo según `errores[]` |
| `429` | Demasiadas solicitudes | Esperar los segundos de la cabecera `Retry-After` |

**Ejemplo `422`**

```json
{
  "type": "https://api.klintec.example/errores/validacion",
  "title": "Datos de entrada inválidos",
  "status": 422,
  "trace_id": "9f8e7d6c5b4a",
  "errores": [
    {
      "campo": "superficies[0].area_m2",
      "codigo": "VALOR_NO_POSITIVO",
      "mensaje": "El área debe ser mayor que 0."
    },
    {
      "campo": "comercial.margen_neto_pct",
      "codigo": "PORCENTAJE_FUERA_DE_RANGO",
      "mensaje": "El margen debe estar entre 0 y 50."
    }
  ]
}
```

`errores[].campo` usa notación de ruta (`superficies[0].area_m2`) para ubicar el input exacto.

**Códigos de error por campo:** `VALOR_NO_POSITIVO`, `CAMPO_OBLIGATORIO`, `UNIDAD_INCOMPATIBLE`, `PORCENTAJE_FUERA_DE_RANGO`.

---

## 7. Advertencias en respuestas exitosas

Una respuesta `200` puede traer `advertencias[]`. No impiden el cálculo, pero el frontend debe mostrarlas junto al resultado.

| Campo | Descripción |
|---|---|
| `codigo` | Ej.: `DILUCION_AMBIGUA`, `PARAMETRO_CADUCADO`, `OVERRIDE_RENDIMIENTO` |
| `mensaje` | Texto para el usuario |
| `severidad` | `info`, `advertencia`, `critica` |
| `campo` | Ruta del campo relacionado (opcional) |

Sugerencia de UI: `info` en gris, `advertencia` en amarillo, `critica` en rojo y con confirmación antes de guardar.

---

## 8. Tipos reutilizables

**Monto**

```
string con patrón ^-?\d+\.\d{2}$      Ejemplo: "803.73"
```

**Porcentaje**

```
number entre 0 y 100                  Ejemplo: 10  (equivale a 10 %)
```

**TipoInfraestructura**

```
hospital | oficina | centro_comercial | institucion_educativa | industria | otro
```

**EstadoCotizacion**

```
borrador | en_revision | aprobada | rechazada | enviada
```

**ConvencionDilucion**

```
partes_agua     → 1 parte de producto + D de agua  → fracción = 1/(1+D)
solucion_total  → 1 parte de producto en D totales → fracción = 1/D
```

---

## 9. Reglas de oro para el frontend

1. **No recalcular** ningún valor monetario ni cantidad en el cliente; solo mostrar lo que devuelve la API.
2. **Mostrar el dinero como string**, sin convertirlo a `float`. Si se necesita formato, usar una librería de decimales.
3. **Validar en cliente** solo lo básico (obligatorios, > 0, rangos de `limites`). La validación definitiva es la del servidor.
4. **Mostrar siempre** `supuestos` y `advertencias` junto al precio.
5. **Mostrar `version_parametros`** en la cotización para que sea claro con qué valores se calculó.
6. **Usar `Idempotency-Key`** al guardar, para no duplicar si el usuario hace doble clic.
7. **Deshabilitar la edición** cuando `estado` sea `aprobada` o `enviada`.
8. **Guardar el `trace_id`** de los errores para soporte.

---

## 10. Pendientes por definir con negocio

| Tema | Estado en este contrato |
|---|---|
| IVA y otros tributos | No incluidos: el cálculo termina en `subtotal_oferta` |
| Margen sobre costo vs. sobre venta | Se aplica como recargo sobre el costo directo, junto con los otros dos porcentajes |
| Recargo nocturno | Se aplica según `proporcion_horas_nocturnas_pct` |
| Doble conteo vacaciones / factor 1,18 | Debe definirse qué cubre cada uno antes de producción |
| Roles y permisos | Propuesta inicial: `cotizador`, `revisor`, `admin`, `auditor` |
| Dominios y correos | De ejemplo (`klintec.example`) |

---

*El contrato formal en OpenAPI 3.1 (`klintec_apu_openapi.yaml`) es la fuente de verdad para generar clientes y mocks; este documento es su guía de lectura.*

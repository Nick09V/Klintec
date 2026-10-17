# Klintec v2.0
## Cotización técnica, APU auditable y control operativo para Facility Management

> **Mensaje comercial:** Klintec convierte una solicitud operativa de limpieza en una cotización técnico-económica trazable, con costos laborales, químicos, maquinaria y margen calculados de forma determinista.

---

## 1. La oportunidad

Las empresas de limpieza profesional no venden únicamente horas o metros cuadrados. El costo real cambia según:

- tipo de infraestructura y nivel de riesgo;
- rendimiento de cada superficie;
- frecuencia y días de operación;
- cargas laborales y recargos;
- dosificación química;
- desgaste y depreciación de maquinaria;
- margen, riesgo y límites comerciales.

El problema original descrito en `context.md` y `arquitectura.md` es que muchas cotizaciones se construyen con valores planos o planillas difíciles de auditar. Eso puede producir:

1. **subcotización**, cuando el precio no cubre el costo laboral legal;
2. **sobredosificación**, por no calcular concentrados y merma;
3. **maquinaria “gratis”**, al omitir depreciación y mantenimiento;
4. **desconexión entre ventas y operaciones**, cuando el precio negociado no es viable para ejecutar el servicio.

### Propuesta de valor

Klintec reemplaza una cotización opaca por una matriz APU explicable:

> **requerimiento operativo → parámetros → costos verificables → margen → revisión y aprobación**

---

## 2. Qué se planteó originalmente frente a lo que existe hoy

| Capacidad planteada originalmente | Estado actual verificable | Nivel |
|---|---|---|
| Wizard operativo de cuatro pasos | La interfaz tiene navegación P1–P4, formulario de parametrización, desglose técnico, simulador y propuesta formal. | **Implementado en frontend** |
| Estado centralizado del wizard | Zustand conserva proyecto, cliente, tipología, superficies, horarios, turnos, porcentajes, maquinaria, consumibles y gastos. | **Implementado** |
| Catálogos de superficies, químicos, maquinaria y consumibles | Existen endpoints FastAPI y el frontend intenta cargarlos al iniciar P1. | **Implementado con dependencia de backend** |
| Motor APU determinista | Existe un motor Python con cálculos de MOD, CIQ, CMAQ, gastos y consolidación. | **Implementado y probado** |
| Cargas legales laborales | El motor usa SBU 2026, IESS, fondo de reserva, décimos, vacaciones y factor de reemplazo. | **Implementado en el motor** |
| Cálculo de dilución y merma | El motor calcula litros de solución, concentrado y costo químico. | **Implementado y probado** |
| Depreciación de maquinaria | El motor calcula depreciación, mantenimiento y consumibles de desgaste por hora. | **Implementado y probado** |
| APU auditable | La respuesta del motor incluye partidas, unidad, precio unitario, total, fuente y estado de verificación. | **Implementado** |
| Simulador “what-if” | P3 permite modificar admin, riesgo, margen y descuento; el recálculo vuelve a P1. | **Implementado en frontend; requiere motor activo para recalcular** |
| Flujo Operativo–Supervisor | Existe selector de roles, cola local de revisión y acciones de gobernanza en el frontend. | **Parcial** |
| KlinBot RAG / auditoría normativa | Existe un proveedor y endpoint de auditoría con respuestas tipadas y alertas normativas. | **Parcial / MVP** |
| KlinVision y parser SERCOP | Están planteados en la arquitectura y aparecen como superficies de API, pero no hay evidencia de un flujo completo conectado a la UI. | **Futuro** |
| PDF formal con QR y hash | Hay endpoints y lógica inicial de gobernanza/hash; no hay flujo completo de generación y descarga de PDF verificable en el frontend actual. | **Parcial / futuro** |
| Redis, PostgreSQL, pgvector, MinIO y workers | Están definidos como arquitectura objetivo, pero no son necesarios para el flujo mínimo actual y no están demostrados end-to-end en el repositorio actual. | **Futuro** |
| Contrato gold standard de entrada | El frontend tiene `toGoldStandardInput()` y genera las cinco secciones del estándar. | **Implementado en frontend** |
| Integración gold end-to-end | El frontend ya intenta enviar el objeto gold, pero el cliente/backend avanzado todavía conserva tipos y modelos del payload anterior. | **Pendiente de integración** |

### Lectura ejecutiva

Klintec ya tiene un **prototipo funcional del núcleo de cotización**: captura datos, consulta catálogos, calcula costos y presenta un APU explicable. La mayor brecha actual no es matemática, sino de **alineación contractual e integración end-to-end** entre el objeto gold acordado y el endpoint avanzado.

---

## 3. Puntos fuertes actuales

### 3.1 Motor determinista, no una cifra improvisada

El cálculo central está implementado en Python con `Decimal`, validación tipada y fórmulas explícitas. El motor no depende de una respuesta probabilística para determinar el precio.

Incluye:

- mano de obra directa;
- recargo nocturno;
- cargas legales;
- factor de reemplazo por ausentismo;
- químicos y merma;
- maquinaria;
- consumibles y EPP;
- gastos administrativos;
- riesgo;
- margen;
- descuento;
- piso operativo inviolable.

### 3.2 APU con trazabilidad

Cada partida puede devolver:

- identificador;
- categoría;
- descripción;
- unidad;
- cantidad;
- precio unitario;
- total;
- fuente;
- referencia normativa;
- estado de verificación.

Esto permite defender una oferta ante un cliente, un supervisor o un proceso de compras.

### 3.3 Catálogos parametrizables

El frontend no obliga a escribir todos los rendimientos a mano. Consume catálogos de:

- superficies;
- químicos;
- maquinaria;
- consumibles;
- parámetros vigentes.

La arquitectura permite actualizar parámetros sin reescribir las fórmulas del motor.

### 3.4 Protección frente a dumping operativo

El resultado expone si el piso inviolable fue respetado. Además, el backend incluye auditorías para detectar riesgos laborales y precios por debajo del costo operativo directo legal.

### 3.5 Flujo visual orientado a negocio

La experiencia actual separa:

1. **P1:** parametrización;
2. **P2:** desglose técnico APU;
3. **P3:** simulador de margen;
4. **P4:** propuesta y envío a revisión.

Esto hace visible la conversación entre el área comercial y operaciones.

---

## 4. Hechos de la problemática que ya se solventan

### Problema: cotizar solo por metros cuadrados

**Solución actual:** el motor calcula horas requeridas como:

```text
área / rendimiento × frecuencia
```

El rendimiento proviene del catálogo de superficies, por lo que 1.000 m² de una zona crítica no se trata igual que 1.000 m² de una oficina.

### Problema: olvidar obligaciones laborales

**Solución actual:** el caso de prueba del motor incorpora:

- SBU de **USD 482,00**;
- aporte patronal IESS de **12,15%**;
- fondo de reserva;
- décimo tercero;
- décimo cuarto;
- vacaciones;
- factor de reemplazo de **1,18**.

### Problema: desperdicio químico

**Solución actual:** el motor calcula solución preparada, concentrado y merma. En el caso de prueba:

- 1.000 m²;
- 26 días;
- rendimiento de 40 m²/L;
- dilución 1:64;
- merma de 3%;
- costo de concentrado calculado: **USD 154,50**.

### Problema: regalar el uso de maquinaria

**Solución actual:** se calcula depreciación horaria, mantenimiento y desgaste. En el caso de prueba:

- 120 horas mensuales de una fregadora;
- costo calculado: **USD 208,08**.

### Problema: aprobar precios sin revisión operativa

**Solución actual:** existe un selector de rol Operativo/Supervisor, una cola de cotizaciones para revisión y estados como:

- borrador;
- en revisión;
- aprobado;
- cambios solicitados;
- rechazado.

La gobernanza todavía debe consolidarse con persistencia y el flujo de aprobación backend definitivo.

---

## 5. Dato numérico demostrable para la presentación

Los siguientes valores no son una promesa comercial: son el resultado del caso determinista automatizado en `backend/tests/test_engine.py`.

### Caso de prueba: Hospital Metropolitano

Supuestos:

- **1.000 m²** de área crítica;
- rendimiento de **90 m²/h**;
- frecuencia diaria de **1**;
- **26 días** de operación;
- turno nocturno al **100%**;
- químico con dilución **1:64**;
- fregadora compacta durante **120 h/mes**;
- comercial: **10%** administrativo + **5%** riesgo + **15%** margen.

Resultado comprobado:

| Métrica | Resultado |
|---|---:|
| Horas requeridas por día | **11,11 h** |
| Operarios base | **2** |
| Costo mensual por operario con cargas | **USD 841,37** |
| Mano de obra directa | **USD 1.985,64** |
| Químicos, consumibles y EPP | **USD 252,50** |
| Maquinaria | **USD 208,08** |
| Costo operativo directo | **USD 2.446,22** |
| Subtotal de oferta antes de descuento | **USD 3.180,09** |
| Factor comercial aplicado | **1,30** |
| Piso inviolable | **Respetado** |

El repositorio también verifica que el hash del cálculo sea determinista: repetir la misma entrada produce el mismo hash de **16 caracteres**.

### Cómo presentar este dato

> “Para un caso hospitalario de 1.000 m², Klintec no entrega un precio plano: calcula 11,11 horas diarias, dimensiona 2 operarios, incorpora las cargas laborales, estima químicos y maquinaria, y llega a un costo operativo directo verificable de USD 2.446,22.”

---

## 6. Qué está a media implementación

### Integración del contrato gold

El frontend ya construye:

```json
{
  "contrato": {},
  "zonas": [],
  "turnos": [],
  "opciones": {},
  "economicos": {}
}
```

Sin embargo, el backend avanzado y parte de sus tipos todavía fueron construidos alrededor de otro formato (`proyecto`, `periodo`, `superficies`, `comercial`). Antes de una demo integrada se debe:

1. fijar el schema gold como contrato único;
2. actualizar el modelo Pydantic de entrada;
3. adaptar el endpoint de cálculo;
4. probar frontend → API → motor con el mismo fixture;
5. eliminar o versionar explícitamente el payload legado.

### Datos del gold aún no capturados completamente por pantalla

El adaptador actual usa valores predeterminados para algunos campos que el wizard avanzado no expone todavía como controles completos:

- sector;
- tipo de contrato;
- plazo;
- fecha de inicio;
- riesgo;
- superficie exacta;
- suciedad;
- obstáculos;
- turno detallado;
- operación de feriados;
- IVA.

La estructura sí se genera, pero la captura debe ampliarse para que el usuario controle todos los valores.

### Catálogos cuando se ejecuta solo el frontend

Los botones de agregar superficie, maquinaria y consumibles dependen de que los catálogos lleguen desde el backend. En modo frontend aislado:

- las llamadas de catálogo fallan;
- las listas quedan vacías;
- los botones aparecen deshabilitados;
- no se puede generar el cálculo real.

Para una demo offline se necesita una de estas opciones:

- fixtures/mock locales;
- modo demo;
- backend levantado con semillas.

### Gobernanza y persistencia

La cola de revisión funciona en el cliente, pero la persistencia robusta, usuarios, permisos, historial y sellado formal deben terminarse en backend.

---

## 7. Roadmap futuro

### Fase 1 — Cerrar el contrato operativo

- Unificar frontend, schema, endpoint y Pydantic bajo `gold_standard_input.json`.
- Validar el fixture gold automáticamente en CI.
- Capturar todos los campos gold desde P1–P3.
- Definir cómo se representan gastos varios, maquinaria y consumibles que no están en el estándar.

### Fase 2 — Demo autónoma y confiable

- Agregar modo demo con catálogos locales.
- Permitir probar el wizard sin conexión al backend.
- Mostrar claramente cuándo el usuario está en modo demo.
- Añadir validación frontend con Zod o React Hook Form, según el flujo definitivo.

### Fase 3 — Gobernanza empresarial

- Persistencia de cotizaciones.
- Usuarios y permisos por rol.
- Auditoría completa de cambios.
- Aprobación, solicitud de cambios y rechazo desde API.
- Hash y QR verificables.

### Fase 4 — Inteligencia operativa

- KlinBot conectado a normativa y fuentes citables.
- KlinVision para inspección visual.
- Parser de pliegos/TDR del SERCOP.
- Recomendación de químicos, maquinaria y rendimientos.

### Fase 5 — Producto comercial

- PDF formal generado desde la cotización aprobada.
- Integración con almacenamiento de documentos.
- Métricas de ahorro, margen y tiempo por cliente.
- Multiempresa y multiusuario.
- Despliegue cloud con observabilidad y respaldo.

---

## 8. Guion de demo de ventas

### Escena 1 — El problema

“Una cotización plana por metro cuadrado no distingue entre una oficina y un quirófano. Klintec comienza por la operación real.”

### Escena 2 — P1

Seleccionar tipología, superficie, área, frecuencia, horario y parámetros comerciales.

### Escena 3 — P2

Mostrar:

- MOD;
- químicos;
- maquinaria;
- costo directo;
- partidas APU;
- fuentes y advertencias.

### Escena 4 — P3

Modificar margen o descuento y explicar el impacto comercial. El sistema conserva el escenario y permite recalcular.

### Escena 5 — P4

Mostrar el snapshot del objeto gold standard y enviar la cotización a revisión.

### Cierre

> “Klintec no solo calcula cuánto cobrar. Explica por qué ese precio es técnicamente necesario, laboralmente defendible y operativamente ejecutable.”

---

## 9. Mensajes comerciales permitidos y mensajes que deben evitarse

### Se puede afirmar hoy

- Existe un motor APU determinista implementado.
- Hay pruebas automatizadas de MOD, CIQ, CMAQ, consolidación, advertencias y hash.
- El frontend tiene un wizard de cuatro pasos.
- El sistema presenta partidas APU con fuentes y estado de verificación.
- Se modelan cargas laborales, químicos, maquinaria y margen.
- Existe una base de flujo Operativo–Supervisor.

### No se debe afirmar todavía como producto terminado

- “Integración gold completa” sin haber alineado el endpoint y el modelo backend.
- “KlinVision operativo” como flujo listo para cliente.
- “PDF firmado con QR listo” si no se ha demostrado la generación end-to-end.
- “RAG productivo” si la auditoría actual no está conectada a una base normativa productiva.
- “Reducción medida de 3–5 días a menos de 3 minutos”. Esa cifra pertenece a la propuesta original; todavía debe medirse con usuarios y casos reales.
- “Reducción comprobada de 18–25% de desperdicio”. Es un objetivo/hipótesis de impacto, no una métrica validada en producción.

---

## 10. Conclusión ejecutiva

Klintec ya demuestra el núcleo de valor: **una cotización de limpieza deja de ser una cifra empírica y se convierte en una estructura de costos explicable**.

El proyecto cuenta con:

- frontend avanzado;
- wizard de cuatro pasos;
- motor determinista;
- catálogos paramétricos;
- cálculo laboral, químico y de maquinaria;
- APU auditable;
- simulador comercial;
- base de gobernanza.

La prioridad para pasar de prototipo sólido a producto demostrable end-to-end es cerrar una sola fuente de verdad para el contrato de entrada, especialmente el estándar gold, y completar el flujo de backend, persistencia, auditoría y propuesta formal.


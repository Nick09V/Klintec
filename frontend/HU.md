Historia de Usuario (HU-02)
Como usuario en la demo del Hackathon, necesito alternar en 1 clic entre la vista de Cotizador / Operativo Comercial y Supervisor de Operaciones sin cerrar sesión.

Tareas Técnicas

Maquetar en Next.js 14.2 + Tailwind + shadcn/ui el layout corporativo B2B.

Implementar Topbar con Role Switcher en vivo (Operativo Comercial <-> Supervisor de Operaciones) y badges de estado de la cotización.

Construir navegación guiada del Wizard de 4 pasos.

Historia de Usuario (HU-02)
Como Operativo Comercial, quiero seleccionar la tipología de infraestructura, cargar plantillas reales o autocompletar con pliego PDF / foto KlinVision.

Tareas Técnicas

Tarjetas interactivas para las 4 Tipologías Oficiales (Hospitalaria/Crítica, Educativa, Corporativa/Comercial, Industrial/Logística).

Formulario dinámico de superficies, metrajes (m²), frecuencias y turnos (Diurno, Nocturno, 24/7) validado con React Hook Form + Zod.

Botones de acción rápida: Cargar Caso Hospital Metropolitano, Importar Pliego SERCOP (PDF) y Autocompletar con Foto (KlinVision).

Historia de Usuario (HU-02)
Como usuario técnico, necesito inspeccionar la tabla de Análisis de Precios Unitarios (APU) filtrable por Nómina, Químicos, Maquinaria y EPP con su referencia legal.

Tareas Técnicas

Construir tabla APU con tabs de filtro (Todos, Mano de Obra MOD, Químicos CIQ, Maquinaria CMAQ, Bioseguridad EPP).

Mostrar rendimiento ISSA aplicado, factor de dilución química, desglose patronal IESS 12,15% y piso salarial SBU $482.

Historia de Usuario (HU-02)
Como Operativo Comercial, quiero simular el margen de utilidad y descuentos de negociación sin perforar jamás el Costo Operativo Directo Legal.

Tareas Técnicas

Sliders interactivos para Gastos Administrativos, Imprevistos y Margen Neto.

Implementar Candado de Piso Legal FEDELIMP (Zona Roja Bloqueada de Dumping Laboral) que impide reducir el precio bajo MOD + CIQ + CMAQ.

Botones de Mesa de Negociación en Vivo (-3% y -5% de descuento) mostrando el impacto en utilidad neta mientras blinda el 100% de la nómina.

Historia de Usuario (HU-04)
Como Supervisor de Operaciones, quiero visualizar mi bandeja ejecutiva y disponer de las 4 acciones de gobernanza junto al panel auditor de KlinBot.

Tareas Técnicas

Construir Bandeja Ejecutiva del Supervisor con KPIs (cotizaciones en revisión, margen neto promedio, alertas de riesgo).

Implementar la barra de 4 Acciones de Gobernanza: 1. Auditar con KlinBot, 2. Aceptar y Sellar (APPROVED), 3. Mandar a Corregir (CHANGES_REQUESTED), 4. Rechazar (REJECTED).

Construir Drawer / Panel Lateral de KlinBot mostrando el dictamen RAG con severidad de alertas y citas normativas.
# INFORME MAESTRO: HACKATHON EXPO CLEAN ECUADOR 2026

 
**Proyecto:** Klintec
**Área:** Gestión Inteligente de Procesos
**Reto Oficial:** Reto 2 – Sistema dinámico de cotización y estructuración de costos unitarios según tipología de infraestructura
**Capitán / Product Owner:** Nick Valverde

 

# I. Ficha Técnica del Evento y Premios

 

1. **Organización:** Feria Internacional Expo Clean Ecuador 2026, con el respaldo gremial de FEDELIMP (Federación Nacional de Empresas de Limpieza y Afines del Ecuador), JIMCORPSERVI, UAO, Escuela Politécnica Nacional, Conquito y LACIF (Unión Europea).

2. **Sede:** Centro de Exposiciones Quito (pabellón posterior asignado con pantallas, mesas y tomas eléctricas).

3. **Fechas presenciales:** Viernes 16 y Sábado 17 de octubre de 2026.

4. **Fondo de Premios Directos (USD 40.000 en total):**

5. La competencia no premia únicamente a 3 proyectos de todo el evento, sino a **12 proyectos premiados (3 por cada Área Estratégica)**:

- **1.er Lugar de Gestión Inteligente de Procesos:** USD 5.000 en efectivo.
- **2.º Lugar de Gestión Inteligente de Procesos:** USD 3.000 en efectivo.
- **3.er Lugar de Gestión Inteligente de Procesos:** USD 2.000 en efectivo.

  6. **Programa y Fondo de Aceleración (Etapa Posterior):**

- Proceso de 12 semanas (enero a marzo) para madurar la solución hacia un producto comercial B2B con soporte de mentores sectoriales.
- Cuenta con una bolsa adicional de hasta **USD 20.000** distribuida según clasificación para financiar servidores, desarrollo, pruebas piloto y prototipado (hasta $10.000 para el primer lugar).

  7. **Propiedad Intelectual:** Permanece **100% en manos de los integrantes del equipo**. No hay cesión de derechos patrimoniales sobre el software desarrollado.

 

# II. El Dolor Real de la Industria (El Problema que Resolvemos)

 

1. **La falla del cálculo plano por metro cuadrado:** En el mercado ecuatoriano de servicios de limpieza y facility management no existe un estándar técnico unificado. Limpiar 1.000 m² de oficinas corporativas no requiere el mismo tiempo ni insumos que 1.000 m² de un patio de comidas con alta rotación de grasa o un área hospitalaria/quirófano con estándares de desinfección microbiológica.

2. **El riesgo financiero:** La mano de obra representa entre el 60% y 70% del costo total. Si un cotizador olvida calcular en una hoja de cálculo el factor de reemplazo (cobertura por descanso semanal/enfermedad) o las cargas sociales de ley (IESS, décimos, fondos de reserva), la empresa gana la licitación pero asume pérdidas financieras durante todo el año de vigencia del contrato.

3. **El desfase comercial vs. operativo:** El departamento de ventas tarda días en estructurar una propuesta económica y suele recortar costos sin consultar con los supervisores de operaciones, comprometiendo la calidad del servicio y la bioseguridad.

 

# III. La Solución Técnica: Arquitectura y Flujo de Klintec

 
Klintec se estructurará como una aplicación web interactiva orientada a resolver este flujo en tres pasos:

 

```text
┌─────────────────────────────────────────────────────────────┐
│ ENTRADA DE REQUERIMIENTOS │
│ - Metraje total por tipo de superficie (piso/vidrio/baños) │
│ - Tipología: Corporativo, Comercial o Crítico/Hospitalario │
│ - Turnos requeridos (diurnos, nocturnos) y tránsito │
└──────────────────────────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ MOTOR PARAMÉTRICO (BACKEND) │
│ - Cálculo de Horas-Hombre + Normativa Laboral (IESS) │
│ - Dosificación de químicos (dilución y consumo por m²) │
│ - Amortización de maquinaria (abrillantadoras/hidrolavadoras)│
└──────────────────────────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DASHBOARD & RESULTADOS │
│ - Desglose transparente de costos unitarios directos/ind. │
│ - Slider interactivo para simular el % de Margen de Utilidad│
│ - Generación en 1 clic de la Propuesta Técnica en PDF │
└─────────────────────────────────────────────────────────────┘
```

 

## Stack Tecnológico Propuesto

 

1. **Frontend:** Next.js / React con Tailwind CSS y componentes prediseñados para acelerar el desarrollo; Recharts para visualizar la proporción de costos (mano de obra vs. insumos vs. maquinaria).

2. **Backend:** Python (FastAPI) para procesar las fórmulas paramétricas de costeo y exponer endpoints REST limpios.

3. **Base de Datos:** PostgreSQL con tablas normalizadas para rendimientos de químicos, tablas salariales y tipologías de infraestructura.

4. **Motor de Documentos:** Generación dinámica de propuestas técnico-comerciales en PDF listo para firmar.

 

# IV. Reglas Críticas y Gobernanza del Hackathon

 

1. **Autorización de desarrollo previo:** La coordinación general (Mónica Sevilla) confirmó que **los equipos pueden llegar con bases de código, esquemas de diseño y arquitecturas preconfiguradas** para acelerar el desarrollo del MVP in situ.

2. **Datos para la demo:** La organización no entrega datasets. Cada equipo debe llevar sus datos simulados y tablas de cálculo listas.

3. **Criterios de Evaluación y Desempate (Matriz de 100 puntos):**

- **Prototipo, demo o simulación práctica (20%):** Es el criterio con mayor peso numérico. Si hay un empate entre dos equipos, **se desempata comparando directamente este criterio**.
- Comprensión del problema (15%).
- Innovación de la solución (15%).
- Viabilidad técnica (15%).
- Impacto potencial (15%).
- Calidad de la presentación / Pitch (10%).
- Proceso y trabajo en equipo (10%).

  4. **Composición del Tribunal:** Siete jurados calificarán de forma independiente. Estará compuesto por empresarios de FEDELIMP, académicos (EPN y UAO), delegados institucionales (LACIF) y entidades públicas (SERCOP, SECAP, IESS, Ministerios de Trabajo, Ambiente y Producción).

  5. **Políticas estrictas de asistencia:**

- Se permite como máximo un **20% de ausencia justificada por jornada** (por exámenes o citas médicas, notificadas por correo). Faltar media jornada o una jornada completa implica descalificación del equipo.
- **Pitch final:** La exposición puede darla uno o varios integrantes, pero **todo el equipo debe subir y estar físicamente en el escenario** durante la defensa; de lo contrario, el equipo queda eliminado automáticamente.
- No se admiten cambios de integrantes durante las jornadas del 16 y 17 de octubre.

  6. **Pases e invitados:** La acreditación cubre a los integrantes oficiales más **5 pases de cortesía** para invitados en el momento del pitch y la deliberación.

"use client";

import { useEffect, useState } from "react";
import TopBar from "@/components/TopBar";
import SupervisorDashboard from "@/components/SupervisorDashboard";
import KlinBotDrawer from "@/components/KlinBotDrawer";
import { api, ApiError } from "@/lib/api";
import {
  QuoteCalculationResponse,
  ConsumableCatalogItem,
} from "@/lib/api-types";
import { cn, fmtMoney, fmtNumber, INFRASTRUCTURE_LABELS, TYPOLOGIES } from "@/lib/constants";
import { useQuoteStore, type QuoteInput } from "@/store/useQuoteStore";
import { createReviewQuote, loadReviewQuotes, ReviewQuote, saveReviewQuotes } from "@/lib/supervisor-queue";

function Icon({ children }: { children: string }) {
  return <span className="material-symbols-outlined align-middle">{children}</span>;
}

function SectionTitle({ eyebrow, title, description }: { eyebrow: string; title: string; description?: string }) {
  return <div className="mb-6"><p className="text-label-caps uppercase text-secondary">{eyebrow}</p><h1 className="mt-1 font-headline text-display-lg">{title}</h1>{description && <p className="mt-2 max-w-3xl text-body-md text-on-surface-variant">{description}</p>}</div>;
}

function MoneyCard({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return <div className="card p-4"><p className="text-label-caps uppercase text-on-surface-variant">{label}</p><p className="mt-2 font-mono-metric text-mono-metric-lg">{fmtMoney(value)}</p>{detail && <p className="mt-1 text-body-sm text-on-surface-variant">{detail}</p>}</div>;
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const fields = error.problem.errores?.map((item) => `${item.campo}: ${item.mensaje}`).join(" ");
    return `${error.message}${fields ? ` ${fields}` : ""}${error.problem.trace_id ? ` (trace_id: ${error.problem.trace_id})` : ""}`;
  }
  return "No fue posible conectar con el motor de cotización.";
}

function ContractSetup({ onContinue }: { onContinue: () => void }) {
  const state = useQuoteStore();
  const contract = state.contract;
  const [tdrLoading, setTdrLoading] = useState(false);
  const [tdrMessage, setTdrMessage] = useState("");

  async function handleTdrUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setTdrLoading(true);
    setTdrMessage("Analizando pliego TDR con Gemini...");
    try {
      const tdr = await api.ingestTdr(file);
      state.applyTdrData(tdr);
      setTdrMessage(`✓ Pliego procesado con Gemini: ${tdr.resumen}. ${tdr.metrajes.length} zonas y frecuencias precargadas.`);
    } catch {
      setTdrMessage("No fue posible extraer datos del pliego TDR. Puedes continuar manualmente.");
    } finally {
      setTdrLoading(false);
    }
  }

  return <div className="step-enter">
    <SectionTitle
      eyebrow="Paso 00 / Datos del contrato"
      title="Define el contrato antes de parametrizar"
      description="Estos datos alimentan directamente el bloque contrato del objeto quote_input."
    />
    <div className="mb-6 rounded-xl border border-secondary/30 bg-secondary-fixed/40 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-headline font-semibold text-body-md flex items-center gap-2">
            <Icon>picture_as_pdf</Icon>
            ¿Tienes los Términos de Referencia (TDR) o Pliego SERCOP?
          </p>
          <p className="text-body-sm text-on-surface-variant">
            Sube el PDF (~50 páginas) y Gemini precargará entidad, código, zonas, metrajes y turnos.
          </p>
        </div>
        <label className="btn-secondary flex cursor-pointer items-center gap-2">
          <Icon>upload_file</Icon>
          <span>{tdrLoading ? "Procesando pliego..." : "Importar Pliego TDR (PDF)"}</span>
          <input
            type="file"
            accept="application/pdf"
            disabled={tdrLoading}
            onChange={(e) => void handleTdrUpload(e)}
            className="hidden"
          />
        </label>
      </div>
      {tdrMessage && (
        <p className="mt-3 rounded-lg bg-surface p-2.5 text-body-sm font-medium text-secondary">
          {tdrMessage}
        </p>
      )}
    </div>
    <section className="card p-5">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <label className="text-body-sm">Sector
          <select className="input-numeric mt-1 w-full" value={contract.sector} onChange={(e) => state.updateContract({ sector: e.target.value as QuoteInput["contrato"]["sector"] })}>
            <option value="privado">Privado</option><option value="publico">Público</option>
          </select>
        </label>
        <label className="text-body-sm">Tipo de contrato
          <select className="input-numeric mt-1 w-full" value={contract.tipo} onChange={(e) => state.updateContract({ tipo: e.target.value as QuoteInput["contrato"]["tipo"] })}>
            <option value="recurrente">Recurrente</option><option value="unico">Único</option>
          </select>
        </label>
        <label className="text-body-sm">Cliente
          <input className="input-numeric mt-1 w-full" required value={contract.cliente} onChange={(e) => { state.updateContract({ cliente: e.target.value }); state.setClientName(e.target.value); }} />
        </label>
        <label className="text-body-sm">Tipología
          <select className="input-numeric mt-1 w-full" value={contract.tipologia} onChange={(e) => state.updateContract({ tipologia: e.target.value as QuoteInput["contrato"]["tipologia"] })}>
            <option value="hospitalaria">Hospitalaria</option><option value="educativa">Educativa</option><option value="corporativa">Corporativa</option><option value="industrial">Industrial</option><option value="otra">Otra</option>
          </select>
        </label>
        <label className="text-body-sm">Plazo (meses)
          <select className="input-numeric mt-1 w-full" value={contract.plazo_meses} onChange={(e) => state.updateContract({ plazo_meses: Number(e.target.value) })}>
            {[1, 3, 6, 12, 24].map((months) => <option key={months} value={months}>{months}</option>)}
          </select>
        </label>
        <label className="text-body-sm">Fecha de inicio
          <input className="input-numeric mt-1 w-full" type="date" value={contract.fecha_inicio} onChange={(e) => state.updateContract({ fecha_inicio: e.target.value })} />
        </label>
        <label className="text-body-sm">Código de proceso
          <input className="input-numeric mt-1 w-full" value={contract.codigo_proceso || ""} onChange={(e) => state.updateContract({ codigo_proceso: e.target.value })} />
        </label>
        <label className="text-body-sm">Presupuesto referencial
          <input className="input-numeric mt-1 w-full" type="number" min="0" value={contract.presupuesto_referencial ?? ""} onChange={(e) => state.updateContract({ presupuesto_referencial: e.target.value ? Number(e.target.value) : undefined })} />
        </label>
        <label className="flex items-center gap-2 pt-6 text-body-sm">
          <input type="checkbox" checked={contract.urgente || false} onChange={(e) => state.updateContract({ urgente: e.target.checked })} />
          Contrato urgente
        </label>
      </div>
      <button type="button" onClick={onContinue} disabled={!contract.cliente.trim() || !contract.fecha_inicio} className="btn-primary mt-6">
        Continuar a P1 <Icon>arrow_forward</Icon>
      </button>
    </section>
  </div>;
}

function StepOne({ onCalculate }: { onCalculate: (result: QuoteCalculationResponse, payload: QuoteInput) => void }) {
  const state = useQuoteStore();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [catalogError, setCatalogError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([api.getSurfaces(), api.getChemicals(), api.getMachinery(), api.getConsumables(), api.getParameters()])
      .then(([surfaces, chemicals, machinery, consumables, parameters]) => {
        if (!active) return;
        const current = useQuoteStore.getState();
        current.setCatalogs({ surfaces: surfaces.items, chemicals: chemicals.items, machinery: machinery.items, consumables: consumables.items, parameters });
        if (current.surfaces.length === 0) {
          current.setSurfaces(surfaces.items.slice(0, 1).map((surface) => ({
            id: surface.id,
            catalogId: surface.id,
            name: surface.nombre,
            area: 600,
            frequency: 1,
            color: "bg-secondary",
            chemicalId: chemicals.items[0]?.id || "",
            zoneType: "general",
            risk: "general",
            surface: "vinilo",
            dirt: "media",
            level: "estandar",
            obstacles: "bajo",
            method: "manual",
            frequencyCode: "diaria_1",
            machineId: null,
          })));
        }
      })
      .catch((error: unknown) => setCatalogError(errorMessage(error)));
    return () => { active = false; };
  }, []);

  async function calculate() {
    setLoading(true);
    setMessage("");
    const goldPayload = state.toGoldStandardInput();
    const calcPayload = state.toCalculationRequest();
    try {
      const response = await api.calculateQuote(calcPayload);
      onCalculate(response, goldPayload);
      state.setCurrentStep(2);
      setMessage("Cálculo determinista APU actualizado correctamente.");
    } catch (error) {
      setMessage(errorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  function selectSurface(surfaceId: string, catalogId: string) {
    const catalogSurface = state.catalogs.surfaces.find((item) => item.id === catalogId);
    if (catalogSurface) {
      state.updateSurface(surfaceId, { catalogId: catalogSurface.id, name: catalogSurface.nombre });
    }
  }

  return <div className="step-enter">
    <SectionTitle eyebrow="Paso 01 / Ingesta técnica" title="Parametrización de instalaciones" description="Los catálogos y parámetros vigentes alimentan el contrato del motor. El frontend no calcula importes." />
    {catalogError && <div className="mb-5 rounded-lg bg-red-100 px-4 py-3 text-body-sm text-red-900">{catalogError}</div>}
    {message && <div className="mb-5 rounded-lg bg-secondary-fixed px-4 py-3 text-body-sm text-on-secondary-fixed-variant">{message}</div>}
    <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
      <div className="card p-5">
        <h2 className="font-headline text-headline-md">Proyecto y tipología</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <input className="input-numeric w-full" value={state.projectName} onChange={(e) => state.setProjectName(e.target.value)} placeholder="Nombre del proyecto" />
          <input className="input-numeric w-full" value={state.clientName} onChange={(e) => state.setClientName(e.target.value)} placeholder="Cliente (opcional)" />
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {TYPOLOGIES.map((type) => <button key={type.code} onClick={() => state.setInfrastructureType(type.code)} className={cn("rounded-lg border p-3 text-left", state.infrastructureType === type.code ? "border-secondary bg-secondary-fixed" : "border-outline-variant")}><Icon>{type.icon}</Icon><p className="mt-1 font-headline">{type.name}</p><p className="text-body-sm text-on-surface-variant">{type.description}</p></button>)}
        </div>
        <div className="mt-6 border-t border-outline-variant pt-5">
          <div className="flex items-center justify-between"><h2 className="font-headline text-headline-md">Superficies y frecuencias</h2><span className="font-mono-metric text-secondary">{fmtNumber(state.totalArea())} m²</span></div>
          <div className="mt-3 space-y-3">{state.surfaces.map((surface) => { const chemical = state.catalogs.chemicals.find((item) => item.id === surface.chemicalId); return <div key={surface.id} className="rounded-lg bg-surface-container-low p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-label-caps uppercase text-on-surface-variant">{surface.name}</span>
              <div className="flex items-center gap-2">
                <label className="flex cursor-pointer items-center gap-1 rounded bg-surface px-2.5 py-1 text-xs font-semibold text-secondary hover:bg-secondary hover:text-white transition-colors border border-outline-variant">
                  <Icon>photo_camera</Icon>
                  <span>Foto (KlinVision)</span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      setMessage("Analizando foto con KlinVision (Gemini)...");
                      try {
                        const vision = await api.inspectVision(file);
                        state.applyVisionInspection(surface.id, vision);
                        setMessage(`KlinVision detectó: ${vision.superficie_detectada} (${vision.nivel_riesgo}). Insumo: ${vision.insumo_sugerido}`);
                      } catch {
                        setMessage("No fue posible inspeccionar la foto con KlinVision.");
                      }
                    }}
                  />
                </label>
                {state.surfaces.length > 1 && <button type="button" onClick={() => state.removeSurface(surface.id)} className="text-body-sm text-red-700">Quitar</button>}
              </div>
            </div>
            <div className="grid gap-2 sm:grid-cols-[1fr_100px_100px]"><select aria-label={`Tipo de piso ${surface.name}`} value={surface.catalogId} onChange={(e) => selectSurface(surface.id, e.target.value)} className="w-full rounded bg-surface p-2 text-body-sm">{state.catalogs.surfaces.map((item) => <option key={item.id} value={item.id}>{item.nombre} · {item.rendimiento_m2_h} m²/h</option>)}</select><input aria-label={`Área ${surface.name}`} type="number" min="0.01" value={surface.area} onChange={(e) => state.updateSurface(surface.id, { area: Number(e.target.value) })} className="input-numeric" /><input aria-label={`Frecuencia ${surface.name}`} type="number" min="0.01" value={surface.frequency} onChange={(e) => state.updateSurface(surface.id, { frequency: Number(e.target.value) })} className="input-numeric" /></div>
            <div className="mt-2 grid gap-2 sm:grid-cols-[1fr_auto] sm:items-center"><select aria-label={`Solución química para ${surface.name}`} value={surface.chemicalId} onChange={(e) => state.updateSurface(surface.id, { chemicalId: e.target.value })} className="w-full rounded bg-surface p-2 text-body-sm"><option value="">Sin solución química</option>{state.catalogs.chemicals.map((chemical) => <option key={chemical.id} value={chemical.id}>{chemical.nombre} · {chemical.convencion_dilucion === "partes_agua" ? `1:${chemical.factor_dilucion} (producto + agua)` : `1:${chemical.factor_dilucion} (solución total)`}</option>)}</select>{chemical ? <span className="text-body-sm text-on-surface-variant">Cubre {chemical.rendimiento_m2_por_litro} m²/L · ${chemical.precio_unitario}/{chemical.unidad_precio}</span> : <span className="text-body-sm text-on-surface-variant">Sin consumo químico para esta superficie</span>}</div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              <label className="text-body-sm">Tipo de zona<input className="input-numeric mt-1 w-full" value={surface.zoneType} onChange={(e) => state.updateSurface(surface.id, { zoneType: e.target.value })} /></label>
              <label className="text-body-sm">Riesgo<select className="input-numeric mt-1 w-full" value={surface.risk} onChange={(e) => state.updateSurface(surface.id, { risk: e.target.value as typeof surface.risk })}><option value="critico">Crítico</option><option value="semicritico">Semicrítico</option><option value="no_critico">No crítico</option><option value="alimentos">Alimentos</option><option value="general">General</option></select></label>
              <label className="text-body-sm">Superficie<select className="input-numeric mt-1 w-full" value={surface.surface} onChange={(e) => state.updateSurface(surface.id, { surface: e.target.value as typeof surface.surface })}>{["vinilo", "ceramica", "piedra", "madera", "alfombra", "epoxico", "vidrio", "acero"].map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
              <label className="text-body-sm">Suciedad<select className="input-numeric mt-1 w-full" value={surface.dirt} onChange={(e) => state.updateSurface(surface.id, { dirt: e.target.value as typeof surface.dirt })}><option value="ligera">Ligera</option><option value="media">Media</option><option value="pesada">Pesada</option></select></label>
              <label className="text-body-sm">Nivel<select className="input-numeric mt-1 w-full" value={surface.level} onChange={(e) => state.updateSurface(surface.id, { level: e.target.value as typeof surface.level })}><option value="basico">Básico</option><option value="estandar">Estándar</option><option value="alto">Alto</option></select></label>
              <label className="text-body-sm">Obstáculos<select className="input-numeric mt-1 w-full" value={surface.obstacles} onChange={(e) => state.updateSurface(surface.id, { obstacles: e.target.value as typeof surface.obstacles })}><option value="bajo">Bajo</option><option value="medio">Medio</option><option value="alto">Alto</option></select></label>
              <label className="text-body-sm">Método<select className="input-numeric mt-1 w-full" value={surface.method} onChange={(e) => state.updateSurface(surface.id, { method: e.target.value as typeof surface.method })}><option value="manual">Manual</option><option value="maquina">Máquina</option></select></label>
              <label className="text-body-sm">Frecuencia del contrato<input className="input-numeric mt-1 w-full" value={surface.frequencyCode} onChange={(e) => state.updateSurface(surface.id, { frequencyCode: e.target.value })} placeholder="ej. multidiaria_2" /></label>
              <label className="text-body-sm">Máquina ID (opcional)<input className="input-numeric mt-1 w-full" value={surface.machineId || ""} onChange={(e) => state.updateSurface(surface.id, { machineId: e.target.value || null })} /></label>
            </div>
          </div>; })}</div>
          <button type="button" onClick={() => state.addSurface()} disabled={state.catalogs.surfaces.length === 0} className="btn-ghost mt-3"><Icon>add</Icon>Agregar superficie</button>
          <p className="mt-2 text-body-sm text-on-surface-variant">Cada fila: tipo de piso · área m² · frecuencia diaria · solución química.</p>
        </div>
      </div>
      <aside className="card h-fit p-5">
        <h2 className="font-headline text-headline-md">Operación y parámetros</h2>
        <label className="mt-4 block text-label-caps uppercase text-on-surface-variant">Días de operación al mes</label><input type="number" min="1" max="31" value={state.operatingDays} onChange={(e) => state.setOperatingDays(Number(e.target.value))} className="input-numeric mt-2 w-full" />
        <div className="mt-5 rounded-lg bg-surface-container-low p-4">
          <h3 className="font-headline">Horario para el escenario manual</h3>
          <p className="mt-1 text-body-sm text-on-surface-variant">Indica los días y horas previstos por operario en el mes. El sueldo base se prorratea según las horas regulares declaradas hasta el equivalente a una jornada de 40 horas semanales.</p>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="text-body-sm">Días laborables/mes<input type="number" min="0" max="31" value={state.workdaysPerMonth} onChange={(e) => state.setWorkdaysPerMonth(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label>
            <label className="text-body-sm">Horas por día laborable<input type="number" min="0" max="24" step="0.25" value={state.hoursPerWorkday} onChange={(e) => state.setHoursPerWorkday(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label>
            <label className="text-body-sm">Días de fin de semana/mes<input type="number" min="0" max="31" value={state.weekendDaysPerMonth} onChange={(e) => state.setWeekendDaysPerMonth(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label>
            <label className="text-body-sm">Horas por día de fin de semana<input type="number" min="0" max="24" step="0.25" value={state.hoursPerWeekendDay} onChange={(e) => state.setHoursPerWeekendDay(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label>
          </div>
          <label className="mt-3 block text-body-sm">Horas suplementarias al mes por operario<input type="number" min="0" max="52" step="0.25" value={state.overtimeHoursPerMonth} onChange={(e) => state.setOvertimeHoursPerMonth(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label>
          <p className="mt-2 text-body-sm text-on-surface-variant">Se estima 100% de recargo para trabajo en descanso de fin de semana y 50% para horas suplementarias diurnas. Confirma la modalidad del contrato y descansos.</p>
        </div>
        <label className="mt-4 block text-label-caps uppercase text-on-surface-variant">Turno</label><select value={state.shiftType} onChange={(e) => state.setShiftType(e.target.value as "diurno" | "nocturno" | "mixto")} className="mt-2 w-full rounded-lg bg-surface-container-low p-3"><option value="diurno">Diurno</option><option value="nocturno">Nocturno</option><option value="mixto">Mixto</option></select>
        {state.shiftType === "mixto" && <><label className="mt-4 block text-label-caps uppercase text-on-surface-variant">% horas nocturnas</label><input type="number" min="0" max="100" value={state.nightHoursPct} onChange={(e) => state.setNightHoursPct(Number(e.target.value))} className="input-numeric mt-2 w-full" /></>}
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          <label className="text-body-sm">Inicio del turno<input type="time" className="input-numeric mt-1 w-full" value={state.shiftStart} onChange={(e) => state.setShift({ inicio: e.target.value })} /></label>
          <label className="text-body-sm">Fin del turno<input type="time" className="input-numeric mt-1 w-full" value={state.shiftEnd} onChange={(e) => state.setShift({ fin: e.target.value })} /></label>
          <label className="text-body-sm">Personas<input type="number" min="1" className="input-numeric mt-1 w-full" value={state.shiftPeople} onChange={(e) => state.setShift({ personas: Number(e.target.value) })} /></label>
          <label className="text-body-sm">Días (L,M,X,J,V,S,D)<input className="input-numeric mt-1 w-full" value={state.shiftDays.join(",")} onChange={(e) => state.setShift({ dias: e.target.value.split(",").map((day) => day.trim()).filter(Boolean) })} /></label>
        </div>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          <label className="flex items-center gap-2 text-body-sm"><input type="checkbox" checked={state.operatesHolidays} onChange={(e) => state.setGoldOptions({ opera_feriados: e.target.checked })} />Opera feriados</label>
          <label className="flex items-center gap-2 text-body-sm"><input type="checkbox" checked={state.allowPartial} onChange={(e) => state.setGoldOptions({ permitir_parcial: e.target.checked })} />Permitir parcial</label>
          <label className="flex items-center gap-2 text-body-sm"><input type="checkbox" checked={state.experiencedStaff} onChange={(e) => state.setGoldOptions({ personal_mas_1_anio: e.target.checked })} />Personal con más de 1 año</label>
          <label className="text-body-sm">Ausentismo %<input type="number" min="0" max="100" className="input-numeric mt-1 w-full" value={state.absenteeismPct} onChange={(e) => state.setGoldOptions({ ausentismo_pct: Number(e.target.value) })} /></label>
          <label className="text-body-sm">Horas disponibles<input type="number" min="0.01" className="input-numeric mt-1 w-full" value={state.availableHours} onChange={(e) => state.setGoldOptions({ horas_disponibles: Number(e.target.value) })} /></label>
          <label className="text-body-sm">Personas máximas<input type="number" min="1" className="input-numeric mt-1 w-full" value={state.maximumPeople} onChange={(e) => state.setGoldOptions({ personas_maximas: Number(e.target.value) })} /></label>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4"><label className="text-body-sm">Supervisión %<input type="number" min="0" value={state.adminPct} onChange={(e) => state.setGoldEconomics({ supervision_pct: Number(e.target.value) })} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">Indirectos %<input type="number" min="0" value={state.riskPct} onChange={(e) => state.setGoldEconomics({ indirectos_pct: Number(e.target.value) })} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">Utilidad %<input type="number" min="0" max="99" value={state.marginPct} onChange={(e) => state.setGoldEconomics({ utilidad_pct: Number(e.target.value) })} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">Merma %<input type="number" min="0" value={state.wastePct} onChange={(e) => state.setGoldEconomics({ merma_pct: Number(e.target.value) })} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">IVA %<input type="number" min="0" value={state.vatPct} onChange={(e) => state.setGoldEconomics({ iva_pct: Number(e.target.value) })} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm text-red-800">Descuento %<input type="number" min="0" max="15" value={state.discountPct} onChange={(e) => state.setDiscountPct(Number(e.target.value))} className="input-numeric mt-1 w-full" /><span className="text-xs">No forma parte del schema gold</span></label></div>
        {state.catalogs.parameters && <p className="mt-4 text-body-sm text-on-surface-variant">Parámetros {state.catalogs.parameters.version_parametros} · vigentes desde {state.catalogs.parameters.vigente_desde}</p>}
        <div className="mt-5 border-t border-outline-variant pt-4">
          <p className="text-label-caps uppercase text-on-surface-variant">Maquinaria</p>
          {state.selectedMachinery.map((entry, index) => <div key={`${entry.machineryId}-${index}`} className="mt-2 rounded-lg bg-surface-container-low p-3">
            <div className="flex gap-2"><select aria-label={`Maquinaria ${index + 1}`} value={entry.machineryId} onChange={(e) => state.setSelectedMachinery(state.selectedMachinery.map((item, i) => i === index ? { ...item, machineryId: e.target.value } : item))} className="w-full rounded-lg bg-surface p-3 text-body-sm"><option value="">Selecciona maquinaria</option>{state.catalogs.machinery.map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select><button type="button" onClick={() => state.setSelectedMachinery(state.selectedMachinery.filter((_, i) => i !== index))} aria-label="Quitar maquinaria" className="px-2 text-red-700">×</button></div>
            <input aria-label="Horas de maquinaria al mes" type="number" min="0" value={entry.hours} onChange={(e) => state.setSelectedMachinery(state.selectedMachinery.map((item, i) => i === index ? { ...item, hours: Number(e.target.value) } : item))} className="input-numeric mt-2 w-full" placeholder="Horas de uso mensual" />
          </div>)}
          <button type="button" disabled={state.selectedMachinery.length >= state.catalogs.machinery.length} onClick={() => { const next = state.catalogs.machinery.find((item) => !state.selectedMachinery.some((selected) => selected.machineryId === item.id)); if (next) state.setSelectedMachinery([...state.selectedMachinery, { machineryId: next.id, hours: 0 }]); }} className="btn-ghost mt-2"><Icon>add</Icon>Agregar máquina</button>
          <p className="mt-5 text-label-caps uppercase text-on-surface-variant">Consumibles</p>
          {state.selectedConsumables.map((entry, index) => <div key={`${entry.consumableId}-${index}`} className="mt-2 rounded-lg bg-surface-container-low p-3">
            <div className="flex gap-2"><select aria-label={`Consumible ${index + 1}`} value={entry.consumableId} onChange={(e) => state.setSelectedConsumables(state.selectedConsumables.map((item, i) => i === index ? { ...item, consumableId: e.target.value } : item))} className="w-full rounded-lg bg-surface p-3 text-body-sm"><option value="">Selecciona consumible</option>{(state.catalogs.consumables || []).map((item: ConsumableCatalogItem) => <option key={item.id} value={item.id}>{item.nombre} ({item.unidad})</option>)}</select><button type="button" onClick={() => state.setSelectedConsumables(state.selectedConsumables.filter((_, i) => i !== index))} aria-label="Quitar consumible" className="px-2 text-red-700">×</button></div>
            <input aria-label="Cantidad mensual del consumible" type="number" min="0" value={entry.quantity} onChange={(e) => state.setSelectedConsumables(state.selectedConsumables.map((item, i) => i === index ? { ...item, quantity: Number(e.target.value) } : item))} className="input-numeric mt-2 w-full" placeholder="Cantidad mensual" />
          </div>)}
          <button type="button" disabled={state.selectedConsumables.length >= (state.catalogs.consumables || []).length} onClick={() => { const next = (state.catalogs.consumables || []).find((item: ConsumableCatalogItem) => !state.selectedConsumables.some((selected) => selected.consumableId === item.id)); if (next) state.setSelectedConsumables([...state.selectedConsumables, { consumableId: next.id, quantity: 0 }]); }} className="btn-ghost mt-2"><Icon>add</Icon>Agregar consumible</button>
        </div>
        <div className="mt-5 border-t border-outline-variant pt-4">
          <div className="flex items-center justify-between"><p className="text-label-caps uppercase text-on-surface-variant">Gastos varios</p><span className="font-mono-metric text-secondary">{fmtMoney(state.miscExpenses.reduce((sum, item) => sum + item.amount, 0).toFixed(2))}</span></div>
          <p className="mt-1 text-body-sm text-on-surface-variant">Agrega otros costos mensuales que deban aparecer como partidas del APU.</p>
          {state.miscExpenses.map((expense) => <div key={expense.id} className="mt-3 rounded-lg bg-surface-container-low p-3">
            <div className="flex gap-2"><input aria-label="Detalle del gasto" value={expense.description} onChange={(e) => state.setMiscExpenses(state.miscExpenses.map((item) => item.id === expense.id ? { ...item, description: e.target.value } : item))} className="input-numeric w-full" maxLength={200} placeholder="Detalle del gasto" /><button type="button" onClick={() => state.setMiscExpenses(state.miscExpenses.filter((item) => item.id !== expense.id))} aria-label="Quitar gasto" className="px-2 text-red-700">×</button></div>
            <label className="mt-2 block text-body-sm">Precio mensual<input aria-label="Precio mensual del gasto" type="number" min="0" step="0.01" value={expense.amount} onChange={(e) => state.setMiscExpenses(state.miscExpenses.map((item) => item.id === expense.id ? { ...item, amount: Number(e.target.value) } : item))} className="input-numeric mt-1 w-full" placeholder="0.00" /></label>
          </div>)}
          <button type="button" onClick={() => state.setMiscExpenses([...state.miscExpenses, { id: typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `misc-${Date.now()}`, description: "", amount: 0 }])} className="btn-ghost mt-2"><Icon>add</Icon>Agregar gasto</button>
        </div>
        <button onClick={() => void calculate()} className="btn-primary mt-8 w-full" disabled={loading || state.surfaces.length === 0}>{loading ? "Calculando..." : "Generar matriz APU"}<Icon>arrow_forward</Icon></button>
      </aside>
    </div>
  </div>;
}

function StepTwo({ result, onSubmitForReview, submitted }: { result: QuoteCalculationResponse; onSubmitForReview: () => void; submitted: boolean }) {
  return <div className="step-enter"><SectionTitle eyebrow="Paso 02 / Transparencia de costos" title="Desglose técnico APU" description={`Resultado del motor · parámetros ${result.version_parametros} · hash ${result.hash_calculo}`} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MoneyCard label="MOD" value={result.mod.total} detail={`${result.mod.operarios_base} operarios base`} /><MoneyCard label="CIQ" value={result.ciq.total} detail="Químicos, consumibles y EPP" /><MoneyCard label="CMAQ" value={result.cmaq.total} detail="Depreciación y operación" /><MoneyCard label="Gastos varios" value={result.gastos_varios.total} detail={`${result.gastos_varios.lineas.length} conceptos mensuales`} /></div>
    <div className="mt-6 grid gap-4 lg:grid-cols-2">
      <section className="card p-5"><h2 className="font-headline text-headline-md">Escenario calculado por el sistema</h2><p className="mt-1 text-body-sm text-on-surface-variant">{fmtNumber(result.mod.horas_requeridas_dia)} h/día · {fmtNumber(result.mod.horas_requeridas_mes)} h/mes requeridas · {result.mod.operarios_base} operarios</p><dl className="mt-4 space-y-2 text-body-sm"><div className="flex justify-between"><dt>Costo mensual por operario</dt><dd className="font-mono-metric">{fmtMoney(result.mod.costo_mensual_por_operario.total)}</dd></div><div className="flex justify-between"><dt>Costo total de mano de obra</dt><dd className="font-mono-metric">{fmtMoney(result.mod.total)}</dd></div><div className="flex justify-between"><dt>Costo operativo directo</dt><dd className="font-mono-metric">{fmtMoney(result.consolidacion.costo_operativo_directo)}</dd></div><div className="flex justify-between border-t border-outline-variant pt-2 font-semibold"><dt>Oferta mensual estimada con descuento</dt><dd className="font-mono-metric">{fmtMoney(result.consolidacion.precio_final)}</dd></div></dl></section>
      <section className="card p-5"><h2 className="font-headline text-headline-md">Escenario con tu horario</h2><p className="mt-1 text-body-sm text-on-surface-variant">Laborables: {fmtNumber(result.mod.escenario_usuario.horas_laborables_mes_por_operario)} h · fin de semana: {fmtNumber(result.mod.escenario_usuario.horas_fin_semana_mes_por_operario)} h · suplementarias: {fmtNumber(result.mod.escenario_usuario.horas_extra_mes_por_operario)} h/mes por operario. Total disponible: {fmtNumber(result.mod.escenario_usuario.horas_disponibles_mes_por_operario)} h · {result.mod.escenario_usuario.operarios_requeridos} operarios estimados.</p><dl className="mt-4 space-y-2 text-body-sm"><div className="flex justify-between"><dt>Recargo por fin de semana, por operario</dt><dd className="font-mono-metric">{fmtMoney(result.mod.escenario_usuario.recargo_fin_semana_por_operario)}</dd></div><div className="flex justify-between"><dt>Recargo por horas suplementarias, por operario</dt><dd className="font-mono-metric">{fmtMoney(result.mod.escenario_usuario.recargo_horas_extra_por_operario)}</dd></div><div className="flex justify-between"><dt>Costo mensual total por operario</dt><dd className="font-mono-metric">{fmtMoney(result.mod.escenario_usuario.costo_mensual_por_operario.total)}</dd></div><div className="flex justify-between"><dt>Costo total de mano de obra</dt><dd className="font-mono-metric">{fmtMoney(result.mod.escenario_usuario.total)}</dd></div><div className="flex justify-between"><dt>Costo operativo directo</dt><dd className="font-mono-metric">{fmtMoney(result.consolidacion.costo_operativo_directo_usuario)}</dd></div><div className="flex justify-between border-t border-outline-variant pt-2 font-semibold"><dt>Oferta mensual estimada con descuento</dt><dd className="font-mono-metric">{fmtMoney(result.consolidacion.precio_final_usuario)}</dd></div></dl><p className="mt-3 text-body-sm text-on-surface-variant">Sábados/domingos se asumen como descanso obligatorio trabajado (100%); horas suplementarias diurnas (50%).</p></section>
    </div>
    <div className="card mt-6 overflow-hidden"><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-body-sm"><thead className="bg-surface-container-low text-label-caps uppercase"><tr><th className="p-4">Partida</th><th className="p-4">Unidad</th><th className="p-4 text-right">Unitario</th><th className="p-4 text-right">Total</th><th className="p-4">Fuente</th></tr></thead><tbody>{result.partidas.map((item) => <tr key={item.id} className={cn("border-t border-outline-variant", item.id === "DES-01" && "bg-red-50 text-red-800")}><td className="p-4"><span className="font-mono-metric text-secondary">{item.id}</span><p className="font-semibold">{item.descripcion}</p></td><td className="p-4">{item.unidad}</td><td className="p-4 text-right font-mono-metric">{fmtMoney(item.precio_unitario)}</td><td className="p-4 text-right font-mono-metric font-semibold">{fmtMoney(item.total)}</td><td className="p-4 text-on-surface-variant">{item.fuente}</td></tr>)}</tbody></table></div><div className="flex justify-between border-t border-outline-variant bg-surface-container-low p-4 font-semibold"><span>Costo operativo directo</span><span className="font-mono-metric">{fmtMoney(result.consolidacion.costo_operativo_directo)}</span></div></div>
    <div className="mt-6 grid gap-6 lg:grid-cols-2"><div className="card p-5"><h2 className="font-headline text-headline-md">Consolidación</h2><dl className="mt-3 space-y-2 text-body-sm">{[["Gastos administrativos", result.consolidacion.gastos_administrativos], ["Imprevistos / riesgo", result.consolidacion.imprevistos_riesgo], ["Margen neto", result.consolidacion.margen_neto], ["Subtotal antes del descuento", result.consolidacion.subtotal_oferta]].map(([label, value]) => <div key={label} className="flex justify-between"><dt>{label}</dt><dd className="font-mono-metric">{fmtMoney(value)}</dd></div>)}<div className="flex justify-between text-red-800"><dt>Descuento ({fmtNumber(result.consolidacion.descuento_pct)}%)</dt><dd className="font-mono-metric">−{fmtMoney(result.consolidacion.descuento_comercial)}</dd></div><div className="flex justify-between border-t border-outline-variant pt-2 font-semibold"><dt>Precio final</dt><dd className="font-mono-metric">{fmtMoney(result.consolidacion.precio_final)}</dd></div></dl><p className="mt-4 text-body-sm">{result.consolidacion.piso_inviolable_respetado ? "Piso inviolable respetado." : "Advertencia: el piso inviolable no fue respetado."}</p></div><div className="card p-5"><h2 className="font-headline text-headline-md">Supuestos y advertencias</h2>{result.supuestos.map((item) => <p key={item} className="mt-2 text-body-sm">• {item}</p>)}{result.advertencias.length === 0 ? <p className="mt-2 text-body-sm text-on-surface-variant">Sin advertencias.</p> : result.advertencias.map((item) => <div key={`${item.codigo}-${item.campo}`} className={cn("mt-3 rounded p-3 text-body-sm", item.severidad === "critica" ? "bg-red-100 text-red-900" : item.severidad === "advertencia" ? "bg-amber-100 text-amber-900" : "bg-surface-container-low")}><strong>{item.codigo}</strong><p>{item.mensaje}</p></div>)}</div></div>
    <button type="button" onClick={onSubmitForReview} disabled={submitted} className="btn-primary mt-6">{submitted ? "Enviado a revisión del supervisor" : "Enviar cotización a revisión"}</button>
  </div>;
}

function StepThree({ result, onEdit }: { result: QuoteCalculationResponse; onEdit: () => void }) {
  const state = useQuoteStore();
  const scenario = result.mod.escenario_usuario;

  return <div className="step-enter">
    <SectionTitle
      eyebrow="Paso 03 / Simulador de margen"
      title="Simula tu escenario operativo"
      description="Ajusta los parámetros comerciales y vuelve al paso 1 para recalcular con el motor determinista."
    />
    <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <section className="card p-5">
        <h2 className="font-headline text-headline-md">Parámetros editables</h2>
        <p className="mt-2 text-body-sm text-on-surface-variant">
          Los cambios quedan guardados en el wizard y se aplican al volver a generar la matriz APU.
        </p>
        <div className="mt-5 space-y-4">
          <label className="block text-body-sm">
            Gastos administrativos: <strong>{state.adminPct}%</strong>
            <input type="range" min="0" max="30" step="0.5" value={state.adminPct} onChange={(e) => state.setAdminPct(Number(e.target.value))} className="mt-2 w-full" />
          </label>
          <label className="block text-body-sm">
            Imprevistos / riesgo: <strong>{state.riskPct}%</strong>
            <input type="range" min="0" max="30" step="0.5" value={state.riskPct} onChange={(e) => state.setRiskPct(Number(e.target.value))} className="mt-2 w-full" />
          </label>
          <label className="block text-body-sm">
            Margen neto: <strong>{state.marginPct}%</strong>
            <input type="range" min="0" max="50" step="0.5" value={state.marginPct} onChange={(e) => state.setMarginPct(Number(e.target.value))} className="mt-2 w-full" />
          </label>
          <label className="block text-body-sm">
            Descuento: <strong>{state.discountPct}%</strong>
            <input type="range" min="0" max="15" step="0.5" value={state.discountPct} onChange={(e) => state.setDiscountPct(Number(e.target.value))} className="mt-2 w-full" />
          </label>
        </div>
        <button type="button" onClick={onEdit} className="btn-primary mt-6 w-full">
          <Icon>refresh</Icon>Recalcular matriz APU
        </button>
      </section>
      <section className="card p-5">
        <h2 className="font-headline text-headline-md">Resultado del escenario actual</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <MoneyCard label="Precio final" value={result.consolidacion.precio_final} detail={`${result.consolidacion.descuento_pct}% de descuento`} />
          <MoneyCard label="Costo directo" value={result.consolidacion.costo_operativo_directo} detail="Antes de gastos comerciales" />
          <MoneyCard label="Horas disponibles" value={String(scenario.horas_disponibles_mes_por_operario)} detail="Por operario / mes" />
          <MoneyCard label="Operarios estimados" value={String(scenario.operarios_requeridos)} detail="Según tu horario" />
        </div>
        <div className="mt-6 rounded-lg bg-surface-container-low p-4 text-body-sm">
          <p className="font-semibold">Para aplicar los cambios</p>
          <p className="mt-1 text-on-surface-variant">Pulsa “Recalcular matriz APU”. El wizard te llevará al paso 1 y conservará todos los datos ingresados.</p>
        </div>
      </section>
    </div>
  </div>;
}

function StepFour({ result, input, onSubmitForReview, submitted }: {
  result: QuoteCalculationResponse;
  input: QuoteInput;
  onSubmitForReview: () => void;
  submitted: boolean;
}) {
  return <div className="step-enter">
    <SectionTitle eyebrow="Paso 04 / Propuesta formal" title="Revisa y envía la cotización" description="El snapshot de entrada conserva exactamente el contrato gold standard usado para la propuesta." />
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="card p-5">
        <h2 className="font-headline text-headline-md">Resumen comercial</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <MoneyCard label="Precio final" value={result.consolidacion.precio_final} />
          <MoneyCard label="Piso respetado" value={result.consolidacion.piso_inviolable_respetado ? "Sí" : "No"} />
        </div>
        <button type="button" onClick={onSubmitForReview} disabled={submitted} className="btn-primary mt-6 w-full">
          {submitted ? "Enviado a revisión del supervisor" : "Enviar cotización a revisión"}<Icon>send</Icon>
        </button>
      </section>
      <section className="card p-5">
        <h2 className="font-headline text-headline-md">Objeto de entrada gold standard</h2>
        <pre className="mt-4 max-h-[480px] overflow-auto rounded-lg bg-surface-container-low p-4 text-xs">{JSON.stringify(input, null, 2)}</pre>
      </section>
    </div>
  </div>;
}

export default function HomePage() {
  const [result, setResult] = useState<QuoteCalculationResponse | null>(null);
  const [requestPayload, setRequestPayload] = useState<QuoteInput | null>(null);
  const [reviewQuotes, setReviewQuotes] = useState<ReviewQuote[]>([]);
  const { currentStep, setCurrentStep, activeRole, setGovernanceStatus, toGoldStandardInput } = useQuoteStore();
  useEffect(() => {
    const savedQuotes = loadReviewQuotes();
    setReviewQuotes(savedQuotes);
    if (savedQuotes[0]) setGovernanceStatus(savedQuotes[0].status);
  }, [setGovernanceStatus]);
  function updateQuotes(next: ReviewQuote[]) {
    setReviewQuotes(next);
    saveReviewQuotes(next);
    if (next[0]) setGovernanceStatus(next[0].status);
  }
  function submitForReview() {
    if (!result || !requestPayload || reviewQuotes.some((item) => item.result.hash_calculo === result.hash_calculo)) return;
    updateQuotes([createReviewQuote(requestPayload, result), ...reviewQuotes]);
  }
  const isSubmitted = Boolean(result && reviewQuotes.some((item) => item.result.hash_calculo === result.hash_calculo));
  const renderWizardStep = () => {
    if (currentStep === 0) {
      return <ContractSetup onContinue={() => setCurrentStep(1)} />;
    }
    if (!result || currentStep === 1) {
      return <StepOne onCalculate={(calculation, payload) => { setResult(calculation); setRequestPayload(payload); }} />;
    }
    if (currentStep === 2) {
      return <StepTwo result={result} onSubmitForReview={submitForReview} submitted={isSubmitted} />;
    }
    if (currentStep === 3) {
      return <StepThree result={result} onEdit={() => setCurrentStep(1)} />;
    }
    return <StepFour result={result} input={toGoldStandardInput()} onSubmitForReview={submitForReview} submitted={isSubmitted} />;
  };

  return (
    <>
      <TopBar />
      <KlinBotDrawer />
      <main className="mx-auto max-w-[1440px] px-4 pb-12 pt-28 lg:px-8">
        {activeRole === "SUPERVISOR" ? (
          <SupervisorDashboard quotes={reviewQuotes} onChange={updateQuotes} />
        ) : (
          renderWizardStep()
        )}
      </main>
    </>
  );
}

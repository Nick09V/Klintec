"use client";

import { useEffect, useState } from "react";
import TopBar from "@/components/TopBar";
import { api, ApiError } from "@/lib/api";
import {
  QuoteCalculationRequest,
  QuoteCalculationResponse,
} from "@/lib/api-types";
import { cn, fmtMoney, fmtNumber, INFRASTRUCTURE_LABELS, TYPOLOGIES } from "@/lib/constants";
import { useQuoteStore } from "@/store/useQuoteStore";

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

function StepOne({ onCalculate }: { onCalculate: (result: QuoteCalculationResponse) => void }) {
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
          current.setSurfaces(surfaces.items.map((surface, index) => ({
            id: surface.id,
            catalogId: surface.id,
            name: surface.nombre,
            area: index === 0 ? 600 : 200,
            frequency: 1,
            color: ["bg-secondary", "bg-on-tertiary-container", "bg-on-primary-container", "bg-outline"][index % 4],
            chemicalId: chemicals.items[0]?.id || "",
          })));
        }
      })
      .catch((error: unknown) => setCatalogError(errorMessage(error)));
    return () => { active = false; };
  }, []);

  async function calculate() {
    setLoading(true);
    setMessage("");
    const payload: QuoteCalculationRequest = {
      proyecto: { nombre: state.projectName, cliente: state.clientName || undefined, tipo_infraestructura: state.infrastructureType },
      periodo: { dias_operacion_mes: state.operatingDays },
      turno: { tipo: state.shiftType, proporcion_horas_nocturnas_pct: state.nightHoursPct },
      bonificacion_especialidad: state.specialtyBonus,
      superficies: state.surfaces.map((surface) => ({ superficie_id: surface.catalogId, area_m2: surface.area, frecuencia_diaria: surface.frequency, quimico_id: surface.chemicalId || undefined })),
      maquinaria: state.selectedMachinery.map((item) => ({ maquinaria_id: item.machineryId, horas_uso_mensual: item.hours })),
      consumibles: state.selectedConsumables.map((item) => ({ consumible_id: item.consumableId, cantidad_mensual: item.quantity })),
      comercial: { gastos_administrativos_pct: state.adminPct, imprevistos_riesgo_pct: state.riskPct, margen_neto_pct: state.marginPct },
      version_parametros: state.catalogs.parameters?.version_parametros,
    };
    try {
      onCalculate(await api.calculateQuote(payload));
      state.setCurrentStep(2);
      setMessage("Cálculo determinista actualizado.");
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
        <div className="mt-6 border-t border-outline-variant pt-5"><div className="flex items-center justify-between"><h2 className="font-headline text-headline-md">Superficies y frecuencias</h2><span className="font-mono-metric text-secondary">{fmtNumber(state.totalArea())} m²</span></div><div className="mt-3 space-y-3">{state.surfaces.map((surface) => { const chemical = state.catalogs.chemicals.find((item) => item.id === surface.chemicalId); return <div key={surface.id} className="rounded-lg bg-surface-container-low p-3"><div className="grid gap-2 sm:grid-cols-[1fr_100px_100px] sm:items-center"><select aria-label={`Tipo de piso ${surface.name}`} value={surface.catalogId} onChange={(e) => selectSurface(surface.id, e.target.value)} className="w-full rounded bg-surface p-2 text-body-sm">{state.catalogs.surfaces.map((item) => <option key={item.id} value={item.id}>{item.nombre} · {item.rendimiento_m2_h} m²/h</option>)}</select><input aria-label={`Área ${surface.name}`} type="number" min="0.01" value={surface.area} onChange={(e) => state.updateSurface(surface.id, { area: Number(e.target.value) })} className="input-numeric" /><input aria-label={`Frecuencia ${surface.name}`} type="number" min="0.01" value={surface.frequency} onChange={(e) => state.updateSurface(surface.id, { frequency: Number(e.target.value) })} className="input-numeric" /></div><div className="mt-2 grid gap-2 sm:grid-cols-[1fr_auto] sm:items-center"><select aria-label={`Solución química para ${surface.name}`} value={surface.chemicalId} onChange={(e) => state.updateSurface(surface.id, { chemicalId: e.target.value })} className="w-full rounded bg-surface p-2 text-body-sm"><option value="">Sin solución química</option>{state.catalogs.chemicals.map((chemical) => <option key={chemical.id} value={chemical.id}>{chemical.nombre} · {chemical.convencion_dilucion === "partes_agua" ? `1:${chemical.factor_dilucion} (producto + agua)` : `1:${chemical.factor_dilucion} (solución total)`}</option>)}</select>{chemical ? <span className="text-body-sm text-on-surface-variant">Cubre {chemical.rendimiento_m2_por_litro} m²/L · ${chemical.precio_unitario}/{chemical.unidad_precio}</span> : <span className="text-body-sm text-on-surface-variant">Sin consumo químico para esta superficie</span>}</div></div>; })}</div><p className="mt-2 text-body-sm text-on-surface-variant">Cada fila: tipo de piso · área m² · frecuencia diaria · solución química.</p></div>
      </div>
      <aside className="card h-fit p-5">
        <h2 className="font-headline text-headline-md">Operación y parámetros</h2>
        <label className="mt-4 block text-label-caps uppercase text-on-surface-variant">Días de operación al mes</label><input type="number" min="1" max="31" value={state.operatingDays} onChange={(e) => state.setOperatingDays(Number(e.target.value))} className="input-numeric mt-2 w-full" />
        <label className="mt-4 block text-label-caps uppercase text-on-surface-variant">Turno</label><select value={state.shiftType} onChange={(e) => state.setShiftType(e.target.value as "diurno" | "nocturno" | "mixto")} className="mt-2 w-full rounded-lg bg-surface-container-low p-3"><option value="diurno">Diurno</option><option value="nocturno">Nocturno</option><option value="mixto">Mixto</option></select>
        {state.shiftType === "mixto" && <><label className="mt-4 block text-label-caps uppercase text-on-surface-variant">% horas nocturnas</label><input type="number" min="0" max="100" value={state.nightHoursPct} onChange={(e) => state.setNightHoursPct(Number(e.target.value))} className="input-numeric mt-2 w-full" /></>}
        <div className="mt-5 grid grid-cols-3 gap-2"><label className="text-body-sm">Admin %<input type="number" min="0" max="100" value={state.adminPct} onChange={(e) => state.setAdminPct(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">Riesgo %<input type="number" min="0" max="100" value={state.riskPct} onChange={(e) => state.setRiskPct(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label><label className="text-body-sm">Margen %<input type="number" min="0" max="100" value={state.marginPct} onChange={(e) => state.setMarginPct(Number(e.target.value))} className="input-numeric mt-1 w-full" /></label></div>
        {state.catalogs.parameters && <p className="mt-4 text-body-sm text-on-surface-variant">Parámetros {state.catalogs.parameters.version_parametros} · vigentes desde {state.catalogs.parameters.vigente_desde}</p>}
        <div className="mt-5 border-t border-outline-variant pt-4"><p className="text-label-caps uppercase text-on-surface-variant">Maquinaria y consumibles</p><select aria-label="Maquinaria" value={state.selectedMachinery[0]?.machineryId || ""} onChange={(e) => state.setSelectedMachinery(e.target.value ? [{ machineryId: e.target.value, hours: state.selectedMachinery[0]?.hours || 0 }] : [])} className="mt-2 w-full rounded-lg bg-surface-container-low p-3 text-body-sm"><option value="">Sin maquinaria</option>{state.catalogs.machinery.map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select>{state.selectedMachinery[0] && <input aria-label="Horas de maquinaria al mes" type="number" min="0" value={state.selectedMachinery[0].hours} onChange={(e) => state.setSelectedMachinery([{ ...state.selectedMachinery[0], hours: Number(e.target.value) }])} className="input-numeric mt-2 w-full" placeholder="Horas de uso mensual" />}<select aria-label="Consumible" value={state.selectedConsumables[0]?.consumableId || ""} onChange={(e) => state.setSelectedConsumables(e.target.value ? [{ consumableId: e.target.value, quantity: state.selectedConsumables[0]?.quantity || 0 }] : [])} className="mt-2 w-full rounded-lg bg-surface-container-low p-3 text-body-sm"><option value="">Sin consumibles</option>{state.catalogs.consumables.map((item) => <option key={item.id} value={item.id}>{item.nombre} ({item.unidad})</option>)}</select>{state.selectedConsumables[0] && <input aria-label="Cantidad mensual del consumible" type="number" min="0" value={state.selectedConsumables[0].quantity} onChange={(e) => state.setSelectedConsumables([{ ...state.selectedConsumables[0], quantity: Number(e.target.value) }])} className="input-numeric mt-2 w-full" placeholder="Cantidad mensual" />}</div>
        <button onClick={() => void calculate()} className="btn-primary mt-8 w-full" disabled={loading || state.surfaces.length === 0}>{loading ? "Calculando..." : "Generar matriz APU"}<Icon>arrow_forward</Icon></button>
      </aside>
    </div>
  </div>;
}

function StepTwo({ result }: { result: QuoteCalculationResponse }) {
  return <div className="step-enter"><SectionTitle eyebrow="Paso 02 / Transparencia de costos" title="Desglose técnico APU" description={`Resultado del motor · parámetros ${result.version_parametros} · hash ${result.hash_calculo}`} />
    <div className="grid gap-4 sm:grid-cols-3"><MoneyCard label="MOD" value={result.mod.total} detail={`${result.mod.operarios_base} operarios base`} /><MoneyCard label="CIQ" value={result.ciq.total} detail="Químicos, consumibles y EPP" /><MoneyCard label="CMAQ" value={result.cmaq.total} detail="Depreciación y operación" /></div>
    <div className="card mt-6 overflow-hidden"><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-body-sm"><thead className="bg-surface-container-low text-label-caps uppercase"><tr><th className="p-4">Partida</th><th className="p-4">Unidad</th><th className="p-4 text-right">Unitario</th><th className="p-4 text-right">Total</th><th className="p-4">Fuente</th></tr></thead><tbody>{result.partidas.map((item) => <tr key={item.id} className="border-t border-outline-variant"><td className="p-4"><span className="font-mono-metric text-secondary">{item.id}</span><p className="font-semibold">{item.descripcion}</p></td><td className="p-4">{item.unidad}</td><td className="p-4 text-right font-mono-metric">{fmtMoney(item.precio_unitario)}</td><td className="p-4 text-right font-mono-metric font-semibold">{fmtMoney(item.total)}</td><td className="p-4 text-on-surface-variant">{item.fuente}</td></tr>)}</tbody></table></div><div className="flex justify-between border-t border-outline-variant bg-surface-container-low p-4 font-semibold"><span>Costo operativo directo</span><span className="font-mono-metric">{fmtMoney(result.consolidacion.costo_operativo_directo)}</span></div></div>
    <div className="mt-6 grid gap-6 lg:grid-cols-2"><div className="card p-5"><h2 className="font-headline text-headline-md">Consolidación</h2><dl className="mt-3 space-y-2 text-body-sm">{[["Gastos administrativos", result.consolidacion.gastos_administrativos], ["Imprevistos / riesgo", result.consolidacion.imprevistos_riesgo], ["Margen neto", result.consolidacion.margen_neto], ["Subtotal de oferta", result.consolidacion.subtotal_oferta]].map(([label, value]) => <div key={label} className="flex justify-between"><dt>{label}</dt><dd className="font-mono-metric">{fmtMoney(value)}</dd></div>)}</dl><p className="mt-4 text-body-sm">{result.consolidacion.piso_inviolable_respetado ? "Piso inviolable respetado." : "Advertencia: el piso inviolable no fue respetado."}</p></div><div className="card p-5"><h2 className="font-headline text-headline-md">Supuestos y advertencias</h2>{result.supuestos.map((item) => <p key={item} className="mt-2 text-body-sm">• {item}</p>)}{result.advertencias.length === 0 ? <p className="mt-2 text-body-sm text-on-surface-variant">Sin advertencias.</p> : result.advertencias.map((item) => <div key={`${item.codigo}-${item.campo}`} className={cn("mt-3 rounded p-3 text-body-sm", item.severidad === "critica" ? "bg-red-100 text-red-900" : item.severidad === "advertencia" ? "bg-amber-100 text-amber-900" : "bg-surface-container-low")}><strong>{item.codigo}</strong><p>{item.mensaje}</p></div>)}</div></div>
  </div>;
}

export default function HomePage() {
  const [result, setResult] = useState<QuoteCalculationResponse | null>(null);
  const { currentStep, setCurrentStep } = useQuoteStore();
  return <><TopBar /><main className="mx-auto max-w-[1440px] px-4 pb-12 pt-28 lg:px-8">{!result || currentStep === 1 ? <StepOne onCalculate={setResult} /> : <><StepTwo result={result} /><button onClick={() => setCurrentStep(1)} className="btn-ghost mt-6"><Icon>arrow_back</Icon>Editar datos</button></>}</main></>;
}

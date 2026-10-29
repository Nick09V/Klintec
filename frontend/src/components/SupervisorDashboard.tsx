"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import { fmtMoney } from "@/lib/constants";
import { ReviewQuote } from "@/lib/supervisor-queue";

const STATUS: Record<ReviewQuote["status"], string> = {
  IN_REVIEW: "Pendiente de revisión",
  APPROVED: "Aprobada",
  CHANGES_REQUESTED: "Corrección solicitada",
  REJECTED: "Rechazada",
};

function getError(error: unknown) {
  return error instanceof ApiError ? error.message : "No se pudo completar la operación.";
}

export default function SupervisorDashboard({ quotes, onChange }: { quotes: ReviewQuote[]; onChange: (quotes: ReviewQuote[]) => void }) {
  const [selectedId, setSelectedId] = useState<string | null>(quotes.find((quote) => quote.status === "IN_REVIEW")?.id || quotes[0]?.id || null);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const quote = quotes.find((item) => item.id === selectedId) || quotes[0];
  const pendingCount = quotes.filter((item) => item.status === "IN_REVIEW").length;

  async function audit() {
    if (!quote) return;
    setBusy(true);
    setMessage("");
    try {
      const result = await api.auditQuote({ solicitud: quote.request, calculo: quote.result });
      onChange(quotes.map((item) => item.id === quote.id ? { ...item, audit: result } : item));
    } catch (error) {
      setMessage(getError(error));
    } finally {
      setBusy(false);
    }
  }

  async function decide(action: "APPROVE" | "REQUEST_CHANGES" | "REJECT") {
    if (!quote) return;
    if ((action === "REQUEST_CHANGES" || action === "REJECT") && !comment.trim()) {
      setMessage("Escribe una observación para solicitar correcciones o rechazar la cotización.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const response = await api.transitionQuote(quote.code, action, comment.trim());
      onChange(quotes.map((item) => item.id === quote.id ? {
        ...item,
        status: response.new_status as ReviewQuote["status"],
        comment: comment.trim(),
        approvalHash: response.approval_hash,
      } : item));
      setComment("");
      setMessage(`Estado actualizado: ${STATUS[response.new_status as ReviewQuote["status"]]}.`);
    } catch (error) {
      setMessage(getError(error));
    } finally {
      setBusy(false);
    }
  }

  return <div className="step-enter">
    <div className="mb-6"><p className="text-label-caps uppercase text-secondary">Gobernanza / Revisión</p><h1 className="mt-1 font-headline text-display-lg">Panel del supervisor</h1><p className="mt-2 text-body-md text-on-surface-variant">Revisa cotizaciones enviadas, ejecuta la auditoría de KlinBot y registra una decisión.</p></div>
    <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
      <aside className="card h-fit p-5"><div className="flex items-center justify-between"><h2 className="font-headline text-headline-md">Cotizaciones</h2><span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-900">{pendingCount} pendientes</span></div>
        {quotes.length === 0 ? <p className="mt-4 rounded-lg bg-surface-container-low p-4 text-body-sm text-on-surface-variant">No hay cotizaciones enviadas. Calcula una cotización en el rol Operativo y selecciona “Enviar a revisión”.</p> : <ul className="mt-4 space-y-2">{quotes.map((item) => <li key={item.id}><button type="button" onClick={() => { setSelectedId(item.id); setMessage(""); }} className={`w-full rounded-lg border p-3 text-left ${quote?.id === item.id ? "border-primary bg-primary/5" : "border-outline-variant"}`}><span className="flex items-center justify-between gap-2"><strong className="font-mono-metric text-sm">{item.code}</strong><span className="text-xs text-on-surface-variant">{STATUS[item.status]}</span></span><span className="mt-1 block font-semibold">{item.projectName}</span><span className="mt-1 block text-body-sm text-on-surface-variant">{item.clientName} · {new Date(item.createdAt).toLocaleDateString("es-EC")}</span></button></li>)}</ul>}
      </aside>
      {quote ? <section className="space-y-5">
        <div className="card p-5"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-label-caps uppercase text-on-surface-variant">{quote.code} · {STATUS[quote.status]}</p><h2 className="mt-1 font-headline text-headline-md">{quote.projectName}</h2><p className="mt-1 text-body-sm text-on-surface-variant">Cliente: {quote.clientName} · Enviada {new Date(quote.createdAt).toLocaleString("es-EC")}</p></div><div className="text-right"><p className="text-body-sm text-on-surface-variant">Precio final propuesto</p><p className="font-mono-metric text-mono-metric-lg">{fmtMoney(quote.result.consolidacion.precio_final)}</p></div></div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3"><div className="rounded-lg bg-surface-container-low p-3"><span className="text-body-sm text-on-surface-variant">Costo directo</span><p className="font-mono-metric">{fmtMoney(quote.result.consolidacion.costo_operativo_directo)}</p></div><div className="rounded-lg bg-surface-container-low p-3"><span className="text-body-sm text-on-surface-variant">Descuento</span><p className="font-mono-metric text-red-800">{quote.result.consolidacion.descuento_pct}% · −{fmtMoney(quote.result.consolidacion.descuento_comercial)}</p></div><div className="rounded-lg bg-surface-container-low p-3"><span className="text-body-sm text-on-surface-variant">Hash de cálculo</span><p className="break-all font-mono-metric text-sm">{quote.result.hash_calculo}</p></div></div>
          <details className="mt-4"><summary className="cursor-pointer text-body-sm font-semibold">Ver partidas APU ({quote.result.partidas.length})</summary><div className="mt-3 overflow-x-auto"><table className="w-full text-left text-body-sm"><thead><tr className="border-b border-outline-variant text-on-surface-variant"><th className="py-2">Partida</th><th className="py-2 text-right">Total</th></tr></thead><tbody>{quote.result.partidas.map((item) => <tr key={item.id} className={`border-b border-outline-variant ${item.id === "DES-01" ? "text-red-800" : ""}`}><td className="py-2">{item.id} · {item.descripcion}</td><td className="py-2 text-right font-mono-metric">{fmtMoney(item.total)}</td></tr>)}</tbody></table></div></details>
        </div>
        <div className="card p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-headline text-headline-md">Auditoría KlinBot</h2><p className="mt-1 text-body-sm text-on-surface-variant">Audita el snapshot de solicitud y cálculo de esta cotización.</p></div><button type="button" disabled={busy} onClick={() => void audit()} className="btn-ghost">{busy ? "Procesando..." : quote.audit ? "Actualizar auditoría" : "Auditar con KlinBot"}</button></div>
          {quote.audit ? <div className="mt-4 rounded-lg bg-surface-container-low p-4"><div className="flex flex-wrap justify-between gap-2"><strong>Riesgo general: {quote.audit.riesgo_general}</strong><span className="text-body-sm">{quote.audit.advertencias.length} advertencias</span></div>{quote.audit.advertencias.map((item, i) => <p key={`warning-${i}`} className="mt-2 text-body-sm text-amber-900">• {item}</p>)}<h3 className="mt-3 text-body-sm font-semibold">Recomendaciones</h3>{quote.audit.recomendaciones.map((item, i) => <p key={`rec-${i}`} className="mt-1 text-body-sm">• {item}</p>)}{quote.audit.optimizaciones.map((item, i) => <p key={`opt-${i}`} className="mt-2 text-body-sm text-on-surface-variant">{item.titulo} · ahorro estimado {fmtMoney(item.ahorro_mensual_estimado)}</p>)}</div> : <p className="mt-4 rounded-lg bg-surface-container-low p-3 text-body-sm text-on-surface-variant">Aún no se ejecutó la auditoría.</p>}
        </div>
        <div className="card p-5"><h2 className="font-headline text-headline-md">Decisión de revisión</h2>{quote.comment && <p className="mt-2 rounded-lg bg-amber-50 p-3 text-body-sm">Observación registrada: {quote.comment}</p>}<label className="mt-3 block text-body-sm">Comentario para la cotización<textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={3} maxLength={1000} className="mt-1 w-full rounded-lg bg-surface-container-low p-3" placeholder="Explica qué debe corregirse o el motivo del rechazo." /></label>{message && <p className="mt-3 rounded-lg bg-surface-container-low p-3 text-body-sm">{message}</p>}<div className="mt-4 flex flex-wrap gap-2"><button type="button" disabled={busy || quote.status !== "IN_REVIEW"} onClick={() => void decide("APPROVE")} className="btn-primary">Aprobar</button><button type="button" disabled={busy || quote.status !== "IN_REVIEW"} onClick={() => void decide("REQUEST_CHANGES")} className="rounded-lg bg-amber-100 px-4 py-2 text-sm font-semibold text-amber-900">Solicitar corrección</button><button type="button" disabled={busy || quote.status !== "IN_REVIEW"} onClick={() => void decide("REJECT")} className="rounded-lg bg-red-100 px-4 py-2 text-sm font-semibold text-red-900">Rechazar</button></div>{quote.approvalHash && <p className="mt-3 text-body-sm text-emerald-800">Aprobación registrada · código de verificación {quote.approvalHash}</p>}</div>
      </section> : <div className="card p-8 text-body-sm text-on-surface-variant">Selecciona una cotización para revisar.</div>}
    </div>
  </div>;
}

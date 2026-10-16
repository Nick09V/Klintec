"use client";

import { useQuoteStore } from "@/store/useQuoteStore";

export default function HomePage() {
  const { activeRole, setActiveRole, currentStep, setCurrentStep, governanceStatus } =
    useQuoteStore();

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <div>
          <h1 className="text-xl font-bold text-emerald-400">
            KLINTEC v2.0 — Expo Clean Ecuador 2026
          </h1>
          <p className="text-xs text-slate-400">
            Motor Determinista APU (SBU $482 + IESS 12.15% + Factor 1.18x) & Auditoría KlinBot RAG
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-mono text-amber-300">
            Estado: {governanceStatus}
          </span>
          <div className="flex rounded-lg border border-slate-700 bg-slate-950 p-1 text-xs">
            <button
              onClick={() => setActiveRole("OPERATIVO")}
              className={`rounded-md px-3 py-1.5 font-medium transition ${
                activeRole === "OPERATIVO"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Rol: Operativo Comercial
            </button>
            <button
              onClick={() => setActiveRole("SUPERVISOR")}
              className={`rounded-md px-3 py-1.5 font-medium transition ${
                activeRole === "SUPERVISOR"
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Rol: Supervisor Operaciones
            </button>
          </div>
        </div>
      </header>

      <nav className="grid grid-cols-4 gap-2">
        {[
          { step: 1, label: "1. Instalaciones & KlinVision" },
          { step: 2, label: "2. Matriz Analítica APU" },
          { step: 3, label: "3. Simulador & Candado FEDELIMP" },
          { step: 4, label: "4. Gobernanza, KlinBot & PDF QR" },
        ].map((item) => (
          <button
            key={item.step}
            onClick={() => setCurrentStep(item.step as 1 | 2 | 3 | 4)}
            className={`rounded-lg border p-3 text-left text-xs font-semibold transition ${
              currentStep === item.step
                ? "border-emerald-500 bg-emerald-950/40 text-emerald-300"
                : "border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <p className="text-sm text-slate-300">
          Base modular lista — Vista activa: <strong>{activeRole}</strong> | Paso actual:{" "}
          <strong>Paso {currentStep}</strong>
        </p>
      </section>
    </main>
  );
}

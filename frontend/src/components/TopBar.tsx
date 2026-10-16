"use client";

import { useQuoteStore } from "@/store/useQuoteStore";
import { cn } from "@/lib/constants";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  DRAFT: { label: "Borrador Técnico", color: "bg-secondary" },
  IN_REVIEW: { label: "En Revisión", color: "bg-amber-500" },
  APPROVED: { label: "Aprobado ✓", color: "bg-emerald-500" },
  CHANGES_REQUESTED: { label: "Correcciones", color: "bg-orange-500" },
  REJECTED: { label: "Rechazado", color: "bg-red-500" },
};

export default function TopBar() {
  const {
    activeRole,
    setActiveRole,
    currentStep,
    setCurrentStep,
    governanceStatus,
  } = useQuoteStore();

  const statusInfo = STATUS_LABELS[governanceStatus] || STATUS_LABELS.DRAFT;

  const steps = [
    { step: 1 as const, label: "1. Parametrización" },
    { step: 2 as const, label: "2. Desglose Técnico" },
    { step: 3 as const, label: "3. Simulador de Margen" },
    { step: 4 as const, label: "4. Propuesta Formal" },
  ];

  return (
    <header className="fixed top-0 w-full z-50 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      <div className="h-16 w-full px-4 lg:px-8 flex items-center justify-between gap-4">
        {/* Logo */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-on-primary text-[18px]">
              local_hospital
            </span>
          </div>
          <div className="flex flex-col">
            <span className="font-headline text-headline-sm text-on-surface tracking-tight leading-none">
              Klintec
            </span>
            <span className="font-body text-[10px] uppercase text-secondary tracking-wider mt-0.5">
              v2.0 · Expo Clean 2026
            </span>
          </div>
        </div>

        {/* Step Navigation */}
        <nav className="hidden xl:flex items-center gap-1 bg-surface-container-low px-1 py-1 rounded-xl">
          {steps.map((item) => (
            <button
              key={item.step}
              onClick={() => setCurrentStep(item.step)}
              className={cn(
                "px-4 py-1 font-body text-body-sm transition-all whitespace-nowrap rounded-lg",
                currentStep === item.step
                  ? "bg-primary text-on-primary font-semibold shadow-sm"
                  : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Right section */}
        <div className="flex items-center gap-3 shrink-0">
          {/* Licitación info (desktop only) */}
          <div className="hidden lg:flex flex-col items-end">
            <div className="flex items-center gap-1">
              <span className="font-body text-label-caps text-on-surface-variant uppercase">
                Licitación:
              </span>
              <span className="font-mono-metric text-mono-metric-sm text-on-surface font-semibold">
                SERCOP-HOSP-2026-084
              </span>
            </div>
            <span className="font-body text-body-sm text-on-surface font-medium">
              Hospital Metropolitano Quito
            </span>
          </div>

          {/* Status Badge */}
          <div className="hidden sm:flex items-center gap-1.5 bg-surface-container px-2 py-1 rounded">
            <span
              className={cn(
                "w-2 h-2 rounded-full",
                statusInfo.color,
                governanceStatus === "IN_REVIEW" && "animate-pulse-dot"
              )}
            />
            <span className="font-body text-label-caps uppercase text-on-surface font-medium">
              {statusInfo.label}
            </span>
          </div>

          {/* Role Switcher */}
          <div className="flex rounded-lg bg-surface-container-low p-0.5 text-xs">
            <button
              onClick={() => setActiveRole("OPERATIVO")}
              className={cn(
                "rounded-md px-3 py-1.5 font-headline text-body-sm font-semibold transition-all",
                activeRole === "OPERATIVO"
                  ? "bg-secondary text-on-secondary shadow-sm"
                  : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              Operativo
            </button>
            <button
              onClick={() => setActiveRole("SUPERVISOR")}
              className={cn(
                "rounded-md px-3 py-1.5 font-headline text-body-sm font-semibold transition-all",
                activeRole === "SUPERVISOR"
                  ? "bg-primary text-on-primary shadow-sm"
                  : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              Supervisor
            </button>
          </div>

          {/* User Avatar */}
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-primary text-[18px]">
              person
            </span>
          </div>
        </div>
      </div>

      {/* Mobile step nav */}
      <div className="xl:hidden flex overflow-x-auto gap-1 px-4 pb-2 bg-surface-container-lowest">
        {steps.map((item) => (
          <button
            key={item.step}
            onClick={() => setCurrentStep(item.step)}
            className={cn(
              "px-3 py-1 font-body text-body-sm whitespace-nowrap rounded-lg transition-all shrink-0",
              currentStep === item.step
                ? "bg-primary text-on-primary font-semibold"
                : "text-on-surface-variant bg-surface-container-low"
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
    </header>
  );
}

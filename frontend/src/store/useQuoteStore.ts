import { create } from "zustand";
import {
  ChemicalCatalogItem,
  ConsumableCatalogItem,
  CurrentParameters,
  InfrastructureType,
  MachineryCatalogItem,
  SurfaceCatalogItem,
} from "@/lib/api-types";

export type ActiveRole = "OPERATIVO" | "SUPERVISOR";
export type QuoteGovernanceStatus =
  | "DRAFT"
  | "IN_REVIEW"
  | "APPROVED"
  | "CHANGES_REQUESTED"
  | "REJECTED";

export interface SurfaceEntry {
  id: string;
  catalogId: string;
  name: string;
  area: number;
  frequency: number;
  color: string;
  chemicalId: string;
}

export interface MiscExpenseEntry {
  id: string;
  description: string;
  amount: number;
}

export interface QuoteInput {
  contrato: {
    sector: "privado" | "publico";
    tipo: "recurrente" | "unico";
    cliente: string;
    tipologia: "hospitalaria" | "educativa" | "corporativa" | "industrial" | "otra";
    plazo_meses: number;
    fecha_inicio: string;
  };
  zonas: Array<{
    nombre: string;
    tipo_zona: string;
    riesgo: "critico" | "semicritico" | "no_critico" | "alimentos" | "general";
    superficie: "vinilo" | "ceramica" | "piedra" | "madera" | "alfombra" | "epoxico" | "vidrio" | "acero";
    m2: number;
    suciedad: "ligera" | "media" | "pesada";
    nivel: "basico" | "estandar" | "alto";
    obstaculos: "bajo" | "medio" | "alto";
    metodo: "manual" | "maquina";
    frecuencia: string;
    visitas_mes: number;
    quimico_id: string;
  }>;
  turnos: Array<{ dias: string[]; inicio: string; fin: string; personas: number }>;
  opciones: {
    opera_feriados: boolean;
    permitir_parcial: boolean;
    personal_mas_1_anio: boolean;
    ausentismo_pct: number;
    salario_base: number;
  };
  economicos: {
    supervision_pct: number;
    indirectos_pct: number;
    utilidad_pct: number;
    merma_pct: number;
    iva_pct: number;
  };
}

export interface QuoteStoreState {
  activeRole: ActiveRole;
  currentStep: 1 | 2 | 3 | 4;
  governanceStatus: QuoteGovernanceStatus;
  supervisorNotes: string;
  projectName: string;
  clientName: string;
  infrastructureType: InfrastructureType;
  operatingDays: number;
  workdaysPerMonth: number;
  hoursPerWorkday: number;
  weekendDaysPerMonth: number;
  hoursPerWeekendDay: number;
  overtimeHoursPerMonth: number;
  shiftType: "diurno" | "nocturno" | "mixto";
  nightHoursPct: number;
  specialtyBonus: string;
  adminPct: number;
  riskPct: number;
  marginPct: number;
  discountPct: number;
  surfaces: SurfaceEntry[];
  selectedMachinery: Array<{ machineryId: string; hours: number }>;
  selectedConsumables: Array<{ consumableId: string; quantity: number }>;
  miscExpenses: MiscExpenseEntry[];
  catalogs: {
    surfaces: SurfaceCatalogItem[];
    chemicals: ChemicalCatalogItem[];
    machinery: MachineryCatalogItem[];
    consumables: ConsumableCatalogItem[];
    parameters: CurrentParameters | null;
  };
  setActiveRole: (role: ActiveRole) => void;
  setCurrentStep: (step: 1 | 2 | 3 | 4) => void;
  setProjectName: (value: string) => void;
  setClientName: (value: string) => void;
  setInfrastructureType: (value: InfrastructureType) => void;
  setOperatingDays: (value: number) => void;
  setWorkdaysPerMonth: (value: number) => void;
  setHoursPerWorkday: (value: number) => void;
  setWeekendDaysPerMonth: (value: number) => void;
  setHoursPerWeekendDay: (value: number) => void;
  setOvertimeHoursPerMonth: (value: number) => void;
  setShiftType: (value: "diurno" | "nocturno" | "mixto") => void;
  setNightHoursPct: (value: number) => void;
  setSpecialtyBonus: (value: string) => void;
  setAdminPct: (value: number) => void;
  setRiskPct: (value: number) => void;
  setMarginPct: (value: number) => void;
  setDiscountPct: (value: number) => void;
  setCatalogs: (catalogs: QuoteStoreState["catalogs"]) => void;
  setSurfaces: (surfaces: SurfaceEntry[]) => void;
  addSurface: () => void;
  removeSurface: (id: string) => void;
  updateSurface: (id: string, patch: Partial<SurfaceEntry>) => void;
  setSelectedMachinery: (items: QuoteStoreState["selectedMachinery"]) => void;
  setSelectedConsumables: (items: QuoteStoreState["selectedConsumables"]) => void;
  setMiscExpenses: (items: MiscExpenseEntry[]) => void;
  setGovernanceStatus: (status: QuoteGovernanceStatus) => void;
  totalArea: () => number;
  toGoldStandardInput: () => QuoteInput;
}

const goldStandardZone: QuoteInput["zonas"][number] = {
  nombre: "Quirófanos",
  tipo_zona: "quirofano",
  riesgo: "critico",
  superficie: "vinilo",
  m2: 300,
  suciedad: "media",
  nivel: "estandar",
  obstaculos: "medio",
  metodo: "manual",
  frecuencia: "multidiaria_2",
  visitas_mes: 60,
  quimico_id: "desinf_5g",
};

function tipologiaFromInfrastructure(infrastructureType: InfrastructureType): QuoteInput["contrato"]["tipologia"] {
  if (infrastructureType === "hospital") return "hospitalaria";
  if (infrastructureType === "institucion_educativa") return "educativa";
  if (infrastructureType === "industria") return "industrial";
  if (infrastructureType === "oficina" || infrastructureType === "centro_comercial") return "corporativa";
  return "otra";
}

export const useQuoteStore = create<QuoteStoreState>((set, get) => ({
  activeRole: "OPERATIVO",
  currentStep: 1,
  governanceStatus: "DRAFT",
  supervisorNotes: "",
  projectName: "Oficinas Torre Norte",
  clientName: "",
  infrastructureType: "oficina",
  operatingDays: 26,
  workdaysPerMonth: 22,
  hoursPerWorkday: 8,
  weekendDaysPerMonth: 0,
  hoursPerWeekendDay: 0,
  overtimeHoursPerMonth: 0,
  shiftType: "diurno",
  nightHoursPct: 0,
  specialtyBonus: "0.00",
  adminPct: 10,
  riskPct: 5,
  marginPct: 15,
  discountPct: 0,
  surfaces: [],
  selectedMachinery: [],
  selectedConsumables: [],
  miscExpenses: [],
  catalogs: { surfaces: [], chemicals: [], machinery: [], consumables: [], parameters: null },
  setActiveRole: (activeRole) => set({ activeRole }),
  setCurrentStep: (currentStep) => set({ currentStep }),
  setProjectName: (projectName) => set({ projectName }),
  setClientName: (clientName) => set({ clientName }),
  setInfrastructureType: (infrastructureType) => set({ infrastructureType }),
  setOperatingDays: (operatingDays) => set({ operatingDays: Math.max(1, Math.min(31, operatingDays)) }),
  setWorkdaysPerMonth: (workdaysPerMonth) => set({ workdaysPerMonth: Math.max(0, Math.min(31, workdaysPerMonth)) }),
  setHoursPerWorkday: (hoursPerWorkday) => set({ hoursPerWorkday: Math.max(0, Math.min(24, hoursPerWorkday)) }),
  setWeekendDaysPerMonth: (weekendDaysPerMonth) => set({ weekendDaysPerMonth: Math.max(0, Math.min(31, weekendDaysPerMonth)) }),
  setHoursPerWeekendDay: (hoursPerWeekendDay) => set({ hoursPerWeekendDay: Math.max(0, Math.min(24, hoursPerWeekendDay)) }),
  setOvertimeHoursPerMonth: (overtimeHoursPerMonth) => set({ overtimeHoursPerMonth: Math.max(0, Math.min(52, overtimeHoursPerMonth)) }),
  setShiftType: (shiftType) =>
    set({ shiftType, nightHoursPct: shiftType === "nocturno" ? 100 : shiftType === "diurno" ? 0 : get().nightHoursPct }),
  setNightHoursPct: (nightHoursPct) => set({ nightHoursPct: Math.max(0, Math.min(100, nightHoursPct)) }),
  setSpecialtyBonus: (specialtyBonus) => set({ specialtyBonus }),
  setAdminPct: (adminPct) => set({ adminPct }),
  setRiskPct: (riskPct) => set({ riskPct }),
  setMarginPct: (marginPct) => set({ marginPct }),
  setDiscountPct: (discountPct) => set({ discountPct: Math.max(0, Math.min(15, discountPct)) }),
  setCatalogs: (catalogs) => set({ catalogs }),
  setSurfaces: (surfaces) => set({ surfaces }),
  addSurface: () => set((state) => {
    const catalogSurface = state.catalogs.surfaces[0];
    if (!catalogSurface) return state;
    return { surfaces: [...state.surfaces, {
      id: typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `surface-${Date.now()}-${state.surfaces.length}`,
      catalogId: catalogSurface.id,
      name: catalogSurface.nombre,
      area: 200,
      frequency: 1,
      color: "bg-secondary",
      chemicalId: state.catalogs.chemicals[0]?.id || "",
    }] };
  }),
  removeSurface: (id) => set((state) => ({ surfaces: state.surfaces.filter((surface) => surface.id !== id) })),
  updateSurface: (id, patch) =>
    set((state) => ({
      surfaces: state.surfaces.map((surface) => (surface.id === id ? { ...surface, ...patch } : surface)),
    })),
  setSelectedMachinery: (selectedMachinery) => set({ selectedMachinery }),
  setSelectedConsumables: (selectedConsumables) => set({ selectedConsumables }),
  setMiscExpenses: (miscExpenses) => set({ miscExpenses }),
  setGovernanceStatus: (governanceStatus) => set({ governanceStatus }),
  totalArea: () => get().surfaces.reduce((sum, surface) => sum + surface.area, 0),
  toGoldStandardInput: () => {
    const state = get();
    const zonas = state.surfaces.length === 0
      ? [goldStandardZone]
      : state.surfaces.map((surface) => ({
          ...goldStandardZone,
          nombre: surface.name,
          m2: surface.area,
          frecuencia: surface.frequency === 2 ? "multidiaria_2" : "diaria_1",
          visitas_mes: surface.frequency * state.operatingDays,
          quimico_id: surface.chemicalId || goldStandardZone.quimico_id,
        }));

    return {
      contrato: {
        sector: "privado",
        tipo: "recurrente",
        cliente: state.clientName.trim() || "Clínica San Rafael",
        tipologia: tipologiaFromInfrastructure(state.infrastructureType),
        plazo_meses: 12,
        fecha_inicio: "2026-11-01",
      },
      zonas,
      turnos: [{
        dias: ["L", "M", "X", "J", "V", "S", "D"],
        inicio: "06:00",
        fin: "14:00",
        personas: 1,
      }],
      opciones: {
        opera_feriados: false,
        permitir_parcial: false,
        personal_mas_1_anio: true,
        ausentismo_pct: 8,
        salario_base: Number(state.catalogs.parameters?.laborales.sbu || 482),
      },
      economicos: {
        supervision_pct: state.adminPct,
        indirectos_pct: state.riskPct,
        utilidad_pct: state.marginPct,
        merma_pct: Number(state.catalogs.parameters?.quimicos.merma_pct || 3),
        iva_pct: 15,
      },
    };
  },
}));

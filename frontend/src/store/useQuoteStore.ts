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
  zoneType: string;
  risk: QuoteInput["zonas"][number]["riesgo"];
  surface: QuoteInput["zonas"][number]["superficie"];
  dirt: QuoteInput["zonas"][number]["suciedad"];
  level: QuoteInput["zonas"][number]["nivel"];
  obstacles: QuoteInput["zonas"][number]["obstaculos"];
  method: QuoteInput["zonas"][number]["metodo"];
  frequencyCode: string;
  machineId: string | null;
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
    urgente?: boolean;
    codigo_proceso?: string;
    presupuesto_referencial?: number;
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
    maquina_id?: string | null;
  }>;
  turnos: Array<{ dias: string[]; inicio: string; fin: string; personas: number }>;
  opciones: {
    opera_feriados: boolean;
    permitir_parcial: boolean;
    personal_mas_1_anio: boolean;
    ausentismo_pct: number;
    salario_base: number;
    horas_disponibles?: number;
    personas_maximas?: number;
  };
  economicos: {
    supervision_pct: number;
    indirectos_pct: number;
    utilidad_pct: number;
    merma_pct: number;
    iva_pct: number;
  };
  maquinaria: Array<{ maquinaria_id: string; horas_uso_mensual: number }>;
  consumibles: Array<{ consumible_id: string; cantidad_mensual: number }>;
  gastos_varios: Array<{ descripcion: string; monto_mensual: number }>;
}

export interface QuoteStoreState {
  activeRole: ActiveRole;
  currentStep: 0 | 1 | 2 | 3 | 4;
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
  contract: QuoteInput["contrato"];
  shiftDays: string[];
  shiftStart: string;
  shiftEnd: string;
  shiftPeople: number;
  operatesHolidays: boolean;
  allowPartial: boolean;
  experiencedStaff: boolean;
  absenteeismPct: number;
  availableHours: number;
  maximumPeople: number;
  wastePct: number;
  vatPct: number;
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
  setCurrentStep: (step: 0 | 1 | 2 | 3 | 4) => void;
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
  updateContract: (patch: Partial<QuoteInput["contrato"]>) => void;
  setShift: (patch: Partial<QuoteInput["turnos"][number]>) => void;
  setGoldOptions: (patch: Partial<QuoteInput["opciones"]>) => void;
  setGoldEconomics: (patch: Partial<QuoteInput["economicos"]>) => void;
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
  currentStep: 0,
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
  contract: {
    sector: "privado",
    tipo: "recurrente",
    cliente: "",
    tipologia: "corporativa",
    plazo_meses: 12,
    fecha_inicio: "2026-11-01",
    urgente: false,
    codigo_proceso: "",
    presupuesto_referencial: undefined,
  },
  shiftDays: ["L", "M", "X", "J", "V", "S", "D"],
  shiftStart: "06:00",
  shiftEnd: "14:00",
  shiftPeople: 1,
  operatesHolidays: false,
  allowPartial: false,
  experiencedStaff: true,
  absenteeismPct: 8,
  availableHours: 8,
  maximumPeople: 1,
  wastePct: 3,
  vatPct: 15,
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
  updateContract: (patch) => set((state) => ({ contract: { ...state.contract, ...patch } })),
  setShift: (patch) => set((state) => ({
    shiftDays: patch.dias ?? state.shiftDays,
    shiftStart: patch.inicio ?? state.shiftStart,
    shiftEnd: patch.fin ?? state.shiftEnd,
    shiftPeople: patch.personas ?? state.shiftPeople,
  })),
  setGoldOptions: (patch) => set((state) => ({
    operatesHolidays: patch.opera_feriados ?? state.operatesHolidays,
    allowPartial: patch.permitir_parcial ?? state.allowPartial,
    experiencedStaff: patch.personal_mas_1_anio ?? state.experiencedStaff,
    absenteeismPct: patch.ausentismo_pct ?? state.absenteeismPct,
    availableHours: patch.horas_disponibles ?? state.availableHours,
    maximumPeople: patch.personas_maximas ?? state.maximumPeople,
  })),
  setGoldEconomics: (patch) => set((state) => ({
    adminPct: patch.supervision_pct ?? state.adminPct,
    riskPct: patch.indirectos_pct ?? state.riskPct,
    marginPct: patch.utilidad_pct ?? state.marginPct,
    wastePct: patch.merma_pct ?? state.wastePct,
    vatPct: patch.iva_pct ?? state.vatPct,
  })),
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
      zoneType: "general",
      risk: "general",
      surface: "vinilo",
      dirt: "media",
      level: "estandar",
      obstacles: "bajo",
      method: "manual",
      frequencyCode: "diaria_1",
      machineId: null,
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
    return {
      contrato: {
        ...state.contract,
        cliente: state.contract.cliente.trim() || state.clientName.trim() || "Clínica San Rafael",
        tipologia: state.contract.tipologia || tipologiaFromInfrastructure(state.infrastructureType),
      },
      zonas: state.surfaces.length === 0 ? [goldStandardZone] : state.surfaces.map((surface) => ({
        ...goldStandardZone,
        nombre: surface.name,
        tipo_zona: surface.zoneType,
        riesgo: surface.risk,
        superficie: surface.surface,
        m2: surface.area,
        suciedad: surface.dirt,
        nivel: surface.level,
        obstaculos: surface.obstacles,
        metodo: surface.method,
        frecuencia: surface.frequencyCode,
        visitas_mes: surface.frequency * state.operatingDays,
        quimico_id: surface.chemicalId || goldStandardZone.quimico_id,
        maquina_id: surface.machineId,
      })),
      turnos: [{ dias: state.shiftDays, inicio: state.shiftStart, fin: state.shiftEnd, personas: state.shiftPeople }],
      opciones: {
        opera_feriados: state.operatesHolidays,
        permitir_parcial: state.allowPartial,
        personal_mas_1_anio: state.experiencedStaff,
        ausentismo_pct: state.absenteeismPct,
        salario_base: Number(state.catalogs.parameters?.laborales.sbu || 482),
        horas_disponibles: state.availableHours,
        personas_maximas: state.maximumPeople,
      },
      economicos: {
        supervision_pct: state.adminPct,
        indirectos_pct: state.riskPct,
        utilidad_pct: state.marginPct,
        merma_pct: state.wastePct,
        iva_pct: state.vatPct,
      },
      maquinaria: state.selectedMachinery
        .filter((item) => item.machineryId && item.hours > 0)
        .map((item) => ({
          maquinaria_id: item.machineryId,
          horas_uso_mensual: item.hours,
        })),
      consumibles: state.selectedConsumables
        .filter((item) => item.consumableId && item.quantity > 0)
        .map((item) => ({
          consumible_id: item.consumableId,
          cantidad_mensual: item.quantity,
        })),
      gastos_varios: state.miscExpenses
        .filter((item) => item.description.trim() && item.amount > 0)
        .map((item) => ({
          descripcion: item.description.trim(),
          monto_mensual: item.amount,
        })),
    };
  },
}));

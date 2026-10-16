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

interface QuoteStoreState {
  activeRole: ActiveRole;
  currentStep: 1 | 2 | 3 | 4;
  governanceStatus: QuoteGovernanceStatus;
  supervisorNotes: string;
  projectName: string;
  clientName: string;
  infrastructureType: InfrastructureType;
  operatingDays: number;
  shiftType: "diurno" | "nocturno" | "mixto";
  nightHoursPct: number;
  specialtyBonus: string;
  adminPct: number;
  riskPct: number;
  marginPct: number;
  surfaces: SurfaceEntry[];
  selectedMachinery: Array<{ machineryId: string; hours: number }>;
  selectedConsumables: Array<{ consumableId: string; quantity: number }>;
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
  setShiftType: (value: "diurno" | "nocturno" | "mixto") => void;
  setNightHoursPct: (value: number) => void;
  setSpecialtyBonus: (value: string) => void;
  setAdminPct: (value: number) => void;
  setRiskPct: (value: number) => void;
  setMarginPct: (value: number) => void;
  setCatalogs: (catalogs: QuoteStoreState["catalogs"]) => void;
  setSurfaces: (surfaces: SurfaceEntry[]) => void;
  updateSurface: (id: string, patch: Partial<SurfaceEntry>) => void;
  setSelectedMachinery: (items: QuoteStoreState["selectedMachinery"]) => void;
  setSelectedConsumables: (items: QuoteStoreState["selectedConsumables"]) => void;
  setGovernanceStatus: (status: QuoteGovernanceStatus) => void;
  totalArea: () => number;
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
  shiftType: "diurno",
  nightHoursPct: 0,
  specialtyBonus: "0.00",
  adminPct: 10,
  riskPct: 5,
  marginPct: 15,
  surfaces: [],
  selectedMachinery: [],
  selectedConsumables: [],
  catalogs: { surfaces: [], chemicals: [], machinery: [], consumables: [], parameters: null },
  setActiveRole: (activeRole) => set({ activeRole }),
  setCurrentStep: (currentStep) => set({ currentStep }),
  setProjectName: (projectName) => set({ projectName }),
  setClientName: (clientName) => set({ clientName }),
  setInfrastructureType: (infrastructureType) => set({ infrastructureType }),
  setOperatingDays: (operatingDays) => set({ operatingDays: Math.max(1, Math.min(31, operatingDays)) }),
  setShiftType: (shiftType) =>
    set({ shiftType, nightHoursPct: shiftType === "nocturno" ? 100 : shiftType === "diurno" ? 0 : get().nightHoursPct }),
  setNightHoursPct: (nightHoursPct) => set({ nightHoursPct: Math.max(0, Math.min(100, nightHoursPct)) }),
  setSpecialtyBonus: (specialtyBonus) => set({ specialtyBonus }),
  setAdminPct: (adminPct) => set({ adminPct }),
  setRiskPct: (riskPct) => set({ riskPct }),
  setMarginPct: (marginPct) => set({ marginPct }),
  setCatalogs: (catalogs) => set({ catalogs }),
  setSurfaces: (surfaces) => set({ surfaces }),
  updateSurface: (id, patch) =>
    set((state) => ({
      surfaces: state.surfaces.map((surface) => (surface.id === id ? { ...surface, ...patch } : surface)),
    })),
  setSelectedMachinery: (selectedMachinery) => set({ selectedMachinery }),
  setSelectedConsumables: (selectedConsumables) => set({ selectedConsumables }),
  setGovernanceStatus: (governanceStatus) => set({ governanceStatus }),
  totalArea: () => get().surfaces.reduce((sum, surface) => sum + surface.area, 0),
}));

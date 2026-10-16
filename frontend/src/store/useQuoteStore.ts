import { create } from "zustand";

export type ActiveRole = "OPERATIVO" | "SUPERVISOR";
export type QuoteGovernanceStatus =
  | "DRAFT"
  | "IN_REVIEW"
  | "APPROVED"
  | "CHANGES_REQUESTED"
  | "REJECTED";

interface QuoteStoreState {
  activeRole: ActiveRole;
  currentStep: 1 | 2 | 3 | 4;
  governanceStatus: QuoteGovernanceStatus;
  setActiveRole: (role: ActiveRole) => void;
  setCurrentStep: (step: 1 | 2 | 3 | 4) => void;
  setGovernanceStatus: (status: QuoteGovernanceStatus) => void;
}

export const useQuoteStore = create<QuoteStoreState>((set) => ({
  activeRole: "OPERATIVO",
  currentStep: 1,
  governanceStatus: "DRAFT",
  setActiveRole: (activeRole) => set({ activeRole }),
  setCurrentStep: (currentStep) => set({ currentStep }),
  setGovernanceStatus: (governanceStatus) => set({ governanceStatus }),
}));

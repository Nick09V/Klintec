import {
  ApiProblem,
  CatalogResponse,
  ChemicalCatalogItem,
  ConsumableCatalogItem,
  CurrentParameters,
  MachineryCatalogItem,
  QuoteCalculationResponse,
  QuoteCalculationRequest,
  GovernanceActionResponse,
  KlinBotAuditResponse,
  KlinBotChatResponse,
  KlinVisionResponse,
  TDRResponse,
  SurfaceCatalogItem,
} from "@/lib/api-types";
import type { QuoteInput } from "@/store/useQuoteStore";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  readonly problem: ApiProblem;

  constructor(problem: ApiProblem) {
    super(problem.detail || problem.title || "La solicitud fue rechazada.");
    this.name = "ApiError";
    this.problem = problem;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  const headers: Record<string, string> = {};
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { ...headers, ...(init?.headers as Record<string, string> || {}) },
  });
  if (!response.ok) {
    let problem: ApiProblem = { status: response.status };
    try {
      problem = await response.json();
    } catch {
      problem.detail = `El servidor respondió con HTTP ${response.status}.`;
    }
    throw new ApiError(problem);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getSurfaces: () => request<CatalogResponse<SurfaceCatalogItem>>("/catalogos/superficies"),
  getChemicals: () => request<CatalogResponse<ChemicalCatalogItem>>("/catalogos/quimicos"),
  getMachinery: () => request<CatalogResponse<MachineryCatalogItem>>("/catalogos/maquinaria"),
  getConsumables: () => request<CatalogResponse<ConsumableCatalogItem>>("/catalogos/consumibles"),
  getParameters: () => request<CurrentParameters>("/parametros/vigentes"),
  calculateQuote: (payload: QuoteCalculationRequest | QuoteInput) =>
    request<QuoteCalculationResponse>("/cotizaciones/calcular", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  calculateQuoteV2: (payload: QuoteInput) =>
    request<unknown>("/quotes/v2/calculate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  auditQuote: (quoteSnapshot: unknown) =>
    request<KlinBotAuditResponse>("/klinbot/audit", {
      method: "POST",
      body: JSON.stringify({ quote_snapshot: quoteSnapshot }),
    }),
  chatKlinBot: (message: string, context?: unknown) =>
    request<KlinBotChatResponse>("/klinbot/chat", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    }),
  inspectVision: (file: File, prompt?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (prompt) formData.append("prompt", prompt);
    return request<KlinVisionResponse>("/klinbot/vision", {
      method: "POST",
      body: formData,
    });
  },
  ingestTdr: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<TDRResponse>("/klinbot/ingest-tdr", {
      method: "POST",
      body: formData,
    });
  },
  transitionQuote: (quoteCode: string, action: "APPROVE" | "REQUEST_CHANGES" | "REJECT", comment: string) =>
    request<GovernanceActionResponse>("/governance/transition", {
      method: "POST",
      body: JSON.stringify({ quote_code: quoteCode, actor_role: "SUPERVISOR", action, comment }),
    }),
};

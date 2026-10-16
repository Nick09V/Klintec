import {
  ApiProblem,
  CatalogResponse,
  ChemicalCatalogItem,
  ConsumableCatalogItem,
  CurrentParameters,
  MachineryCatalogItem,
  QuoteCalculationRequest,
  QuoteCalculationResponse,
  SurfaceCatalogItem,
} from "@/lib/api-types";

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
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
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
  calculateQuote: (payload: QuoteCalculationRequest) =>
    request<QuoteCalculationResponse>("/cotizaciones/calcular", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};

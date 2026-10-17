import { QuoteCalculationRequest, QuoteCalculationResponse } from "@/lib/api-types";

export type ReviewStatus = "IN_REVIEW" | "APPROVED" | "CHANGES_REQUESTED" | "REJECTED";

export interface ReviewQuote {
  id: string;
  code: string;
  createdAt: string;
  projectName: string;
  clientName: string;
  request: QuoteCalculationRequest;
  result: QuoteCalculationResponse;
  status: ReviewStatus;
  comment: string;
  approvalHash?: string | null;
  audit?: {
    recomendaciones: string[];
    advertencias: string[];
    riesgo_general: string;
    optimizaciones: Array<{ titulo: string; ahorro_mensual_estimado: string }>;
  };
}

const STORAGE_KEY = "klintec.review-queue.v1";

export function loadReviewQuotes(): ReviewQuote[] {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value ? (JSON.parse(value) as ReviewQuote[]) : [];
  } catch {
    return [];
  }
}

export function saveReviewQuotes(quotes: ReviewQuote[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(quotes));
}

export function createReviewQuote(request: QuoteCalculationRequest, result: QuoteCalculationResponse): ReviewQuote {
  const timestamp = Date.now();
  return {
    id: typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `quote-${timestamp}`,
    code: `KLT-${new Date(timestamp).getFullYear()}-${String(timestamp).slice(-6)}`,
    createdAt: new Date(timestamp).toISOString(),
    projectName: request.proyecto.nombre,
    clientName: request.proyecto.cliente || "Sin cliente indicado",
    request,
    result,
    status: "IN_REVIEW",
    comment: "",
  };
}

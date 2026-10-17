import {
  ApiProblem,
  CatalogResponse,
  ChemicalCatalogItem,
  ConsumableCatalogItem,
  CurrentParameters,
  MachineryCatalogItem,
  QuoteCalculationResponse,
  GovernanceActionResponse,
  KlinBotAuditResponse,
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

interface GoldQuoteResult {
  horas: { trabajo: number; pagadas: number; presencia: number | null };
  personal: { fte: number; operarios: number };
  mod: number;
  ciq: number;
  cmaq: number;
  costo_directo: number;
  equilibrio: number;
  precio: number;
  iva: number;
  total: number;
  semaforo: "verde" | "amarillo" | "rojo";
  lineas_apu: Array<{ rubro: string; detalle: string; valor: number; fuente: string }>;
  alertas: Array<{ codigo: string; nivel: "info" | "aviso" | "critico"; mensaje: string }>;
  params_version: string;
}

function money(value: number): string {
  return value.toFixed(2);
}

function adaptGoldResult(result: GoldQuoteResult): QuoteCalculationResponse {
  const zeroBreakdown = {
    sbu: "0.00",
    bonificacion_especialidad: "0.00",
    recargo_nocturno: "0.00",
    remuneracion_base: "0.00",
    iess_patronal: "0.00",
    fondo_reserva: "0.00",
    decimo_tercero: "0.00",
    decimo_cuarto: "0.00",
    vacaciones: "0.00",
    total: "0.00",
  };
  const modBreakdown = { ...zeroBreakdown, total: money(result.mod) };
  const hash = `${result.params_version}-${result.total.toFixed(2)}-${result.costo_directo.toFixed(2)}`;

  return {
    version_parametros: result.params_version,
    hash_calculo: hash,
    mod: {
      horas_requeridas_dia: result.horas.trabajo / 30,
      horas_requeridas_mes: result.horas.trabajo,
      operarios_base: result.personal.operarios,
      costo_mensual_por_operario: modBreakdown,
      factor_reemplazo_ausentismo: result.personal.fte / result.personal.operarios,
      total: money(result.mod),
      escenario_usuario: {
        horas_laborables_mes_por_operario: 0,
        horas_fin_semana_mes_por_operario: 0,
        horas_extra_mes_por_operario: 0,
        horas_disponibles_mes_por_operario: 0,
        recargo_fin_semana_por_operario: "0.00",
        recargo_horas_extra_por_operario: "0.00",
        operarios_requeridos: result.personal.operarios,
        costo_mensual_por_operario: modBreakdown,
        total: money(result.mod),
      },
    },
    ciq: {
      lineas: [],
      subtotal_quimicos: money(result.ciq),
      subtotal_consumibles: "0.00",
      subtotal_kits_epp: "0.00",
      total: money(result.ciq),
    },
    cmaq: {
      lineas: [],
      total: money(result.cmaq),
    },
    gastos_varios: { lineas: [], total: "0.00" },
    consolidacion: {
      costo_operativo_directo: money(result.costo_directo),
      gastos_administrativos: money(result.equilibrio - result.costo_directo),
      imprevistos_riesgo: "0.00",
      margen_neto: money(result.precio - result.equilibrio),
      factor_total: result.precio / Math.max(result.costo_directo, 1),
      subtotal_oferta: money(result.precio),
      descuento_pct: 0,
      descuento_comercial: "0.00",
      precio_final: money(result.total),
      piso_inviolable_respetado: result.precio >= result.costo_directo,
      costo_operativo_directo_usuario: money(result.costo_directo),
      gastos_administrativos_usuario: "0.00",
      imprevistos_riesgo_usuario: "0.00",
      margen_neto_usuario: "0.00",
      subtotal_oferta_usuario: money(result.precio),
      descuento_comercial_usuario: "0.00",
      precio_final_usuario: money(result.total),
    },
    partidas: result.lineas_apu.map((line, index) => ({
      id: `${line.rubro}-${String(index + 1).padStart(2, "0")}`,
      categoria: line.rubro,
      descripcion: line.detalle,
      unidad: "mes",
      cantidad: 1,
      precio_unitario: money(line.valor),
      total: money(line.valor),
      fuente: line.fuente,
      referencia_normativa: null,
      estado_verificacion: "verificado",
    })),
    supuestos: [],
    advertencias: result.alertas.map((alert) => ({
      codigo: alert.codigo,
      mensaje: alert.mensaje,
      severidad: alert.nivel === "critico" ? "critica" : alert.nivel === "aviso" ? "advertencia" : "info",
      campo: null,
    })),
    fuentes: result.lineas_apu.map((line) => ({
      tipo: "apu",
      referencia: line.fuente,
      version: result.params_version,
    })),
  };
}

export const api = {
  getSurfaces: () => request<CatalogResponse<SurfaceCatalogItem>>("/catalogos/superficies"),
  getChemicals: () => request<CatalogResponse<ChemicalCatalogItem>>("/catalogos/quimicos"),
  getMachinery: () => request<CatalogResponse<MachineryCatalogItem>>("/catalogos/maquinaria"),
  getConsumables: () => request<CatalogResponse<ConsumableCatalogItem>>("/catalogos/consumibles"),
  getParameters: () => request<CurrentParameters>("/parametros/vigentes"),
  calculateQuote: async (payload: QuoteInput) =>
    adaptGoldResult(await request<GoldQuoteResult>("/quotes/v2/calculate", {
      method: "POST",
      body: JSON.stringify(payload),
    })),
  auditQuote: (quoteSnapshot: unknown) =>
    request<KlinBotAuditResponse>("/klinbot/audit", {
      method: "POST",
      body: JSON.stringify({ quote_snapshot: quoteSnapshot }),
    }),
  transitionQuote: (quoteCode: string, action: "APPROVE" | "REQUEST_CHANGES" | "REJECT", comment: string) =>
    request<GovernanceActionResponse>("/governance/transition", {
      method: "POST",
      body: JSON.stringify({ quote_code: quoteCode, actor_role: "SUPERVISOR", action, comment }),
    }),
};

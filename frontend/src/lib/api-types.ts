export type InfrastructureType =
  | "hospital"
  | "oficina"
  | "centro_comercial"
  | "institucion_educativa"
  | "industria"
  | "otro";

export type ShiftType = "diurno" | "nocturno" | "mixto";
export type DilutionConvention = "partes_agua" | "solucion_total";

export interface SurfaceCatalogItem {
  id: string;
  nombre: string;
  rendimiento_m2_h: number;
  fuente: string;
}

export interface ChemicalCatalogItem {
  id: string;
  nombre: string;
  factor_dilucion: number;
  convencion_dilucion: DilutionConvention;
  rendimiento_m2_por_litro: number;
  precio_unitario: string;
  unidad_precio: "litro" | "galon" | "kilogramo";
  ficha_tecnica_url?: string | null;
}

export interface MachineryCatalogItem {
  id: string;
  nombre: string;
  valor_adquisicion: string;
  valor_residual: string;
  vida_util_horas: number;
  mantenimiento_por_hora: string;
  consumibles_desgaste_por_hora: string;
}

export interface ConsumableCatalogItem {
  id: string;
  nombre: string;
  categoria: "consumible" | "kit_epp";
  unidad: string;
  precio_unitario: string;
}

export interface CurrentParameters {
  version_parametros: string;
  vigente_desde: string;
  laborales: {
    sbu: string;
    horas_efectivas_por_turno: number;
    horas_mes_jornada_completa: number;
    divisor_hora_suplementaria: number;
    recargo_nocturno_pct: number;
    recargo_hora_suplementaria_pct: number;
    recargo_hora_fin_semana_pct: number;
    iess_patronal_pct: number;
    fondo_reserva_pct: number;
    decimo_tercero_pct: number;
    decimo_cuarto_monto: string;
    vacaciones_pct: number;
    factor_reemplazo_ausentismo: number;
  };
  quimicos: { merma_pct: number };
  comerciales: {
    gastos_administrativos_pct: number;
    imprevistos_riesgo_pct: number;
    margen_neto_pct: number;
    descuento_pct: number;
    limites: Record<string, { min: number; max: number }>;
  };
}

export interface QuoteCalculationRequest {
  proyecto: {
    nombre: string;
    cliente?: string;
    tipo_infraestructura: InfrastructureType;
  };
  periodo: { dias_operacion_mes: number };
  horario_usuario: {
    dias_laborables_mes: number;
    horas_por_dia_laborable: number;
    dias_fin_semana_mes: number;
    horas_por_dia_fin_semana: number;
    horas_extra_mes: number;
  };
  turno: {
    tipo: ShiftType;
    proporcion_horas_nocturnas_pct: number;
  };
  bonificacion_especialidad: string;
  superficies: Array<{
    superficie_id: string;
    area_m2: number;
    frecuencia_diaria: number;
    rendimiento_m2_h_override?: number;
    quimico_id?: string;
  }>;
  maquinaria: Array<{ maquinaria_id: string; horas_uso_mensual: number }>;
  consumibles: Array<{ consumible_id: string; cantidad_mensual: number }>;
  gastos_varios: Array<{ descripcion: string; monto_mensual: number }>;
  comercial: {
    gastos_administrativos_pct: number;
    imprevistos_riesgo_pct: number;
    margen_neto_pct: number;
    descuento_pct: number;
  };
  version_parametros?: string;
}

export interface MoneyBreakdown {
  sbu: string;
  bonificacion_especialidad: string;
  recargo_nocturno: string;
  remuneracion_base: string;
  iess_patronal: string;
  fondo_reserva: string;
  decimo_tercero: string;
  decimo_cuarto: string;
  vacaciones: string;
  total: string;
}

export interface QuoteCalculationResponse {
  version_parametros: string;
  hash_calculo: string;
  mod: {
    horas_requeridas_dia: number;
    horas_requeridas_mes: number;
    operarios_base: number;
    costo_mensual_por_operario: MoneyBreakdown;
    factor_reemplazo_ausentismo: number;
    total: string;
    escenario_usuario: {
      horas_laborables_mes_por_operario: number;
      horas_fin_semana_mes_por_operario: number;
      horas_extra_mes_por_operario: number;
      horas_disponibles_mes_por_operario: number;
      recargo_fin_semana_por_operario: string;
      recargo_horas_extra_por_operario: string;
      operarios_requeridos: number;
      costo_mensual_por_operario: MoneyBreakdown;
      total: string;
    };
  };
  ciq: {
    lineas: Array<{
      quimico_id: string;
      nombre: string;
      litros_solucion: number;
      litros_concentrado: number;
      convencion_dilucion: DilutionConvention;
      merma_pct: number;
      precio_unitario_litro: string;
      costo: string;
    }>;
    subtotal_quimicos: string;
    subtotal_consumibles: string;
    subtotal_kits_epp: string;
    total: string;
  };
  cmaq: {
    lineas: Array<{
      maquinaria_id: string;
      nombre: string;
      depreciacion_por_hora: string;
      mantenimiento_por_hora: string;
      consumibles_por_hora: string;
      costo_horario: string;
      horas_uso_mensual: number;
      costo: string;
    }>;
    total: string;
  };
  gastos_varios: {
    lineas: Array<{ descripcion: string; monto_mensual: string; costo: string }>;
    total: string;
  };
  consolidacion: {
    costo_operativo_directo: string;
    gastos_administrativos: string;
    imprevistos_riesgo: string;
    margen_neto: string;
    factor_total: number;
    subtotal_oferta: string;
    descuento_pct: number;
    descuento_comercial: string;
    precio_final: string;
    piso_inviolable_respetado: boolean;
    costo_operativo_directo_usuario: string;
    gastos_administrativos_usuario: string;
    imprevistos_riesgo_usuario: string;
    margen_neto_usuario: string;
    subtotal_oferta_usuario: string;
    descuento_comercial_usuario: string;
    precio_final_usuario: string;
  };
  partidas: Array<{
    id: string;
    categoria: string;
    descripcion: string;
    unidad: string;
    cantidad: number;
    precio_unitario: string;
    total: string;
    fuente: string;
    referencia_normativa?: string | null;
    estado_verificacion: string;
  }>;
  supuestos: string[];
  advertencias: Array<{
    codigo: string;
    mensaje: string;
    severidad: "info" | "advertencia" | "critica";
    campo?: string | null;
  }>;
  fuentes: Array<{ tipo: string; referencia: string; version: string }>;
}

export interface KlinBotAuditResponse {
  recomendaciones: string[];
  advertencias: string[];
  riesgo_general: string;
  optimizaciones: Array<{ titulo: string; ahorro_mensual_estimado: string }>;
}

export interface GovernanceActionResponse {
  quote_code: string;
  new_status: "DRAFT" | "IN_REVIEW" | "APPROVED" | "CHANGES_REQUESTED" | "REJECTED";
  pdf_unlocked: boolean;
  watermark_text: string | null;
  approval_hash: string | null;
  qr_verification_url: string | null;
  updated_at: string;
}

export interface ApiProblem {
  title?: string;
  detail?: string;
  status?: number;
  trace_id?: string;
  errores?: Array<{ campo: string; mensaje: string }>;
}

export type CatalogResponse<T> = { items: T[]; total?: number };

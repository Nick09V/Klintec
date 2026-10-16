from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field, model_validator

from .catalog import (
    InfrastructureType, ShiftType, DilutionConvention
)


class Project(BaseModel):
    nombre: str = Field(min_length=3, max_length=150)
    cliente: Optional[str] = Field(default=None, max_length=150)
    tipo_infraestructura: InfrastructureType


class Periodo(BaseModel):
    dias_operacion_mes: int = Field(default=26, ge=1, le=31)


class Turno(BaseModel):
    tipo: ShiftType
    proporcion_horas_nocturnas_pct: float = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def _normalizar(self) -> "Turno":
        # Contrato: 100% si nocturno, 0% si diurno, declarado si mixto.
        if self.tipo == "nocturno":
            self.proporcion_horas_nocturnas_pct = 100.0
        elif self.tipo == "diurno":
            self.proporcion_horas_nocturnas_pct = 0.0
        return self


class SurfaceInput(BaseModel):
    superficie_id: str
    area_m2: float = Field(gt=0)
    frecuencia_diaria: float = Field(gt=0)
    rendimiento_m2_h_override: Optional[float] = Field(default=None, gt=0)
    quimico_id: Optional[str] = None


class MachineryInput(BaseModel):
    maquinaria_id: str
    horas_uso_mensual: float = Field(ge=0)


class ConsumableInput(BaseModel):
    consumible_id: str
    cantidad_mensual: float = Field(ge=0)


class CommercialInput(BaseModel):
    gastos_administrativos_pct: float = Field(default=10.0, ge=0, le=25)
    imprevistos_riesgo_pct: float = Field(default=5.0, ge=0, le=15)
    margen_neto_pct: float = Field(default=15.0, ge=0, le=50)


class QuoteCalculationRequest(BaseModel):
    proyecto: Project
    periodo: Periodo = Periodo()
    turno: Turno
    bonificacion_especialidad: str = "0.00"
    superficies: List[SurfaceInput] = Field(min_length=1)
    maquinaria: List[MachineryInput] = []
    consumibles: List[ConsumableInput] = []
    comercial: CommercialInput
    version_parametros: Optional[str] = None


class MoneyBreakdown(BaseModel):
    sbu: str
    bonificacion_especialidad: str
    recargo_nocturno: str
    remuneracion_base: str
    iess_patronal: str
    fondo_reserva: str
    decimo_tercero: str
    decimo_cuarto: str
    vacaciones: str
    total: str


class ModBlock(BaseModel):
    horas_requeridas_dia: float
    horas_requeridas_mes: float
    operarios_base: int
    costo_mensual_por_operario: MoneyBreakdown
    factor_reemplazo_ausentismo: float
    total: str


class CiqLine(BaseModel):
    quimico_id: str
    nombre: str
    litros_solucion: float
    litros_concentrado: float
    convencion_dilucion: DilutionConvention
    merma_pct: float
    precio_unitario_litro: str
    costo: str


class CiqBlock(BaseModel):
    lineas: List[CiqLine]
    subtotal_quimicos: str
    subtotal_consumibles: str
    subtotal_kits_epp: str
    total: str


class CmaqLine(BaseModel):
    maquinaria_id: str
    nombre: str
    depreciacion_por_hora: str
    mantenimiento_por_hora: str
    consumibles_por_hora: str
    costo_horario: str
    horas_uso_mensual: float
    costo: str


class CmaqBlock(BaseModel):
    lineas: List[CmaqLine]
    total: str


class Consolidacion(BaseModel):
    costo_operativo_directo: str
    gastos_administrativos: str
    imprevistos_riesgo: str
    margen_neto: str
    factor_total: float
    subtotal_oferta: str
    piso_inviolable_respetado: bool


class Partida(BaseModel):
    id: str
    categoria: str
    descripcion: str
    unidad: str
    cantidad: float
    precio_unitario: str
    total: str
    fuente: str
    referencia_normativa: Optional[str] = None
    estado_verificacion: Literal["verificado", "pendiente", "supuesto"] = "verificado"


class Advertencia(BaseModel):
    codigo: str
    mensaje: str
    severidad: Literal["info", "advertencia", "critica"]
    campo: Optional[str] = None


class Fuente(BaseModel):
    tipo: str
    referencia: str
    version: str


class QuoteCalculationResponse(BaseModel):
    version_parametros: str
    hash_calculo: str
    mod: ModBlock
    ciq: CiqBlock
    cmaq: CmaqBlock
    consolidacion: Consolidacion
    partidas: List[Partida]
    supuestos: List[str]
    advertencias: List[Advertencia]
    fuentes: List[Fuente]

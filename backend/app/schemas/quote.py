from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .catalog import (
    InfrastructureType, ShiftType, DilutionConvention
)


class Project(BaseModel):
    nombre: str = Field(min_length=3, max_length=150)
    cliente: Optional[str] = Field(default=None, max_length=150)
    tipo_infraestructura: InfrastructureType


class Periodo(BaseModel):
    dias_operacion_mes: int = Field(default=26, ge=1, le=31)


class HorarioUsuario(BaseModel):
    dias_laborables_mes: int = Field(default=22, ge=0, le=31)
    horas_por_dia_laborable: float = Field(default=8, ge=0, le=24)
    dias_fin_semana_mes: int = Field(default=0, ge=0, le=31)
    horas_por_dia_fin_semana: float = Field(default=0, ge=0, le=24)
    horas_extra_mes: float = Field(default=0, ge=0, le=52)

    @model_validator(mode="after")
    def _validar_capacidad(self) -> "HorarioUsuario":
        dias = self.dias_laborables_mes + self.dias_fin_semana_mes
        horas_regulares = (
            self.dias_laborables_mes * self.horas_por_dia_laborable
            + self.dias_fin_semana_mes * self.horas_por_dia_fin_semana
        )
        if dias > 31:
            raise ValueError("Los días laborables y de fin de semana no pueden superar 31 al mes.")
        if horas_regulares <= 0:
            raise ValueError("El horario debe incluir horas regulares; las horas extra no pueden ser la única jornada.")
        return self


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


class MiscExpenseInput(BaseModel):
    descripcion: str = Field(min_length=1, max_length=200)
    monto_mensual: float = Field(ge=0)

    @field_validator("descripcion")
    @classmethod
    def _descripcion_no_vacia(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El detalle del gasto es obligatorio.")
        return value


class CommercialInput(BaseModel):
    gastos_administrativos_pct: float = Field(default=10.0, ge=0, le=25)
    imprevistos_riesgo_pct: float = Field(default=5.0, ge=0, le=15)
    margen_neto_pct: float = Field(default=15.0, ge=0, le=50)
    descuento_pct: float = Field(default=0.0, ge=0, le=15)


class QuoteCalculationRequest(BaseModel):
    proyecto: Project
    periodo: Periodo = Periodo()
    horario_usuario: HorarioUsuario = HorarioUsuario()
    turno: Turno
    bonificacion_especialidad: str = "0.00"
    superficies: List[SurfaceInput] = Field(min_length=1)
    maquinaria: List[MachineryInput] = []
    consumibles: List[ConsumableInput] = []
    gastos_varios: List[MiscExpenseInput] = []
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


class UserModScenario(BaseModel):
    horas_laborables_mes_por_operario: float
    horas_fin_semana_mes_por_operario: float
    horas_extra_mes_por_operario: float
    horas_disponibles_mes_por_operario: float
    recargo_fin_semana_por_operario: str
    recargo_horas_extra_por_operario: str
    operarios_requeridos: int
    costo_mensual_por_operario: MoneyBreakdown
    total: str


class ModBlock(BaseModel):
    horas_requeridas_dia: float
    horas_requeridas_mes: float
    operarios_base: int
    costo_mensual_por_operario: MoneyBreakdown
    factor_reemplazo_ausentismo: float
    total: str
    escenario_usuario: UserModScenario


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


class MiscExpenseLine(BaseModel):
    descripcion: str
    monto_mensual: str
    costo: str


class MiscExpensesBlock(BaseModel):
    lineas: List[MiscExpenseLine]
    total: str


class Consolidacion(BaseModel):
    costo_operativo_directo: str
    gastos_administrativos: str
    imprevistos_riesgo: str
    margen_neto: str
    factor_total: float
    subtotal_oferta: str
    descuento_pct: float
    descuento_comercial: str
    precio_final: str
    piso_inviolable_respetado: bool
    costo_operativo_directo_usuario: str
    gastos_administrativos_usuario: str
    imprevistos_riesgo_usuario: str
    margen_neto_usuario: str
    subtotal_oferta_usuario: str
    descuento_comercial_usuario: str
    precio_final_usuario: str


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
    gastos_varios: MiscExpensesBlock
    consolidacion: Consolidacion
    partidas: List[Partida]
    supuestos: List[str]
    advertencias: List[Advertencia]
    fuentes: List[Fuente]

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, List, Dict, Any

InfrastructureType = Literal[
    "hospital", "oficina", "centro_comercial", 
    "institucion_educativa", "industria", "otro"
]
ShiftType = Literal["diurno", "nocturno", "mixto"]
DilutionConvention = Literal["partes_agua", "solucion_total"]
CategoryConsumable = Literal["consumible", "kit_epp"]
UnitPrice = Literal["litro", "galon", "kilogramo"]


class SurfaceCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nombre: str
    rendimiento_m2_h: float
    fuente: str


class ChemicalCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nombre: str
    factor_dilucion: float
    convencion_dilucion: DilutionConvention
    rendimiento_m2_por_litro: float
    precio_unitario: str
    unidad_precio: UnitPrice
    ficha_tecnica_url: Optional[str] = None


class MachineryCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nombre: str
    valor_adquisicion: str
    valor_residual: str
    vida_util_horas: int
    mantenimiento_por_hora: str
    consumibles_desgaste_por_hora: str


class ConsumableCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nombre: str
    categoria: CategoryConsumable
    unidad: str
    precio_unitario: str


class LaborParameters(BaseModel):
    sbu: str = Field(description="Salario Básico Unificado 2026 en USD")
    horas_efectivas_por_turno: float = 7.5
    recargo_nocturno_pct: float = 25.0
    iess_patronal_pct: float = 12.15
    fondo_reserva_pct: float = 8.33
    decimo_tercero_pct: float = 8.33
    decimo_cuarto_monto: str = "40.17"
    vacaciones_pct: float = 4.17
    factor_reemplazo_ausentismo: float = 1.18


class ChemicalParameters(BaseModel):
    merma_pct: float = 3.0


class CommercialLimits(BaseModel):
    min: float
    max: float


class CommercialParameters(BaseModel):
    gastos_administrativos_pct: float = 10.0
    imprevistos_riesgo_pct: float = 5.0
    margen_neto_pct: float = 15.0
    limites: Dict[str, CommercialLimits] = {}


class CurrentParameters(BaseModel):
    version_parametros: str
    vigente_desde: str
    laborales: LaborParameters
    quimicos: ChemicalParameters
    comerciales: CommercialParameters


class CatalogResponse(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int = 0
    items: List[Any]
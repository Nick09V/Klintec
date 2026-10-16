from fastapi import APIRouter
from app.seeds.catalog_seed import SURFACES, CHEMICALS, MACHINERY, CONSUMABLES
from app.seeds.parameters_2026 import PARAMETERS_2026
from app.schemas.catalog import (
    SurfaceCatalogItem, ChemicalCatalogItem, MachineryCatalogItem,
    ConsumableCatalogItem, CurrentParameters, CatalogResponse
)

router = APIRouter(prefix="/catalogos", tags=["catalogos"])
parameters_router = APIRouter(prefix="/parametros", tags=["parametros"])


@router.get("/superficies", response_model=CatalogResponse)
def get_surfaces():
    items = [SurfaceCatalogItem(**s).model_dump() for s in SURFACES]
    return CatalogResponse(items=items, total=len(items))


@router.get("/quimicos", response_model=CatalogResponse)
def get_chemicals():
    items = [ChemicalCatalogItem(**c).model_dump() for c in CHEMICALS]
    return CatalogResponse(items=items, total=len(items))


@router.get("/maquinaria", response_model=CatalogResponse)
def get_machinery():
    items = [MachineryCatalogItem(**m).model_dump() for m in MACHINERY]
    return CatalogResponse(items=items, total=len(items))


@router.get("/consumibles", response_model=CatalogResponse)
def get_consumables():
    items = [ConsumableCatalogItem(**cons).model_dump() for cons in CONSUMABLES]
    return CatalogResponse(items=items, total=len(items))


@parameters_router.get("/vigentes", response_model=CurrentParameters)
def get_parameters():
    return CurrentParameters(**PARAMETERS_2026)

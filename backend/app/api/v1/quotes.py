from fastapi import APIRouter, Depends
from app.schemas.quote import QuoteCalculationRequest, QuoteCalculationResponse
from app.services.calc_engine import get_engine, CalculationEngine

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


@router.post("/calcular", response_model=QuoteCalculationResponse)
def calculate_quote(req: QuoteCalculationRequest, engine: CalculationEngine = Depends(get_engine)):
    result = engine.calculate(req)
    return QuoteCalculationResponse(**result)

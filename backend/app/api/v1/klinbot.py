from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.services.klinbot_provider import (
    AuditResponse,
    VisionResponse,
    TDRResponse,
    run_klinbot_audit,
    run_klinbot_chat,
    run_klinvision_inspect,
    run_tdr_parse,
)

router = APIRouter(prefix="/klinbot", tags=["klinbot"])


class AuditRequest(BaseModel):
    quote_snapshot: dict


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    provider: str = "klinbot-copilot"


@router.post("/audit", response_model=AuditResponse)
def audit_quote_endpoint(req: AuditRequest) -> AuditResponse:
    """Audita el snapshot técnico-financiero de una cotización con Gemini / Fallback 2026."""
    return run_klinbot_audit(req.quote_snapshot)


@router.post("/chat", response_model=ChatResponse)
def chat_copilot_endpoint(req: ChatRequest) -> ChatResponse:
    """Chat interactivo en vivo con el Copiloto KlinBot (Gemini)."""
    text = run_klinbot_chat(req.message, req.context)
    return ChatResponse(response=text)


@router.post("/vision", response_model=VisionResponse)
async def vision_inspect_endpoint(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
) -> VisionResponse:
    """Inspección multimodal de imágenes con KlinVision (Gemini Vision)."""
    content = await file.read()
    mime = file.content_type or "image/jpeg"
    return await run_klinvision_inspect(content, mime_type=mime, prompt_extra=prompt)


@router.post("/ingest-tdr", response_model=TDRResponse)
async def ingest_tdr_endpoint(file: UploadFile = File(...)) -> TDRResponse:
    """Extracción estructurada de pliegos SERCOP / TDR en PDF con Gemini."""
    content = await file.read()
    return await run_tdr_parse(content, filename=file.filename or "tdr.pdf")
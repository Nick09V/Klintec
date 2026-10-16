import hashlib
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/governance", tags=["2. Gobernanza Operativo <-> Supervisor"])

QuoteStatus = Literal["DRAFT", "IN_REVIEW", "APPROVED", "CHANGES_REQUESTED", "REJECTED"]
SupervisorAction = Literal["SUBMIT_REVIEW", "APPROVE", "REQUEST_CHANGES", "REJECT"]


class GovernanceActionRequest(BaseModel):
    quote_code: str = "KLT-2026-0001"
    actor_role: Literal["OPERATIVO", "SUPERVISOR"] = "SUPERVISOR"
    action: SupervisorAction
    comment: str = ""


class GovernanceActionResponse(BaseModel):
    quote_code: str
    new_status: QuoteStatus
    pdf_unlocked: bool
    watermark_text: str | None
    approval_hash: str | None
    qr_verification_url: str | None
    updated_at: str


@router.post("/transition", response_model=GovernanceActionResponse)
async def transition_quote_status(payload: GovernanceActionRequest) -> GovernanceActionResponse:
    """
    Maquina de Estados de Gobernanza Ligera (4 acciones del Supervisor).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    mapping: dict[SupervisorAction, QuoteStatus] = {
        "SUBMIT_REVIEW": "IN_REVIEW",
        "APPROVE": "APPROVED",
        "REQUEST_CHANGES": "CHANGES_REQUESTED",
        "REJECT": "REJECTED",
    }
    new_status = mapping[payload.action]
    is_approved = new_status == "APPROVED"

    approval_hash = None
    qr_url = None
    if is_approved:
        raw = f"{payload.quote_code}:{now_iso}:FEDELIMP-IESS-2026"
        approval_hash = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
        qr_url = f"http://localhost:3000/verify/{approval_hash}"

    return GovernanceActionResponse(
        quote_code=payload.quote_code,
        new_status=new_status,
        pdf_unlocked=is_approved,
        watermark_text=None if is_approved else "BORRADOR NO VALIDO - PENDIENTE APROBACION SUPERVISOR",
        approval_hash=approval_hash,
        qr_verification_url=qr_url,
        updated_at=now_iso,
    )

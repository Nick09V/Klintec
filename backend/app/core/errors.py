from __future__ import annotations

import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", None) or str(uuid.uuid4())


def register_exception_handlers(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        request.state.trace_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Trace-Id"] = request.state.trace_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errores = []
        for err in exc.errors():
            loc = [
                str(part) for part in err.get("loc", ())
                if part not in ("body", "QuoteCalculationRequest", "QuoteInput")
            ]
            campo = ""
            for part in loc:
                if part.isdigit():
                    campo += f"[{part}]"
                else:
                    campo += ("." if campo else "") + part
            errores.append({
                "campo": campo or "body",
                "codigo": err.get("type", "VALIDACION"),
                "mensaje": err.get("msg", "valor invalido"),
            })
        return JSONResponse(
            status_code=422,
            media_type="application/problem+json",
            content={
                "type": "https://api.klintec.example/errores/validacion",
                "title": "Datos de entrada invalidos",
                "detail": "Uno o mas campos no cumplen el esquema esperado.",
                "status": 422,
                "trace_id": _trace_id(request),
                "errores": errores,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Error HTTP",
                "detail": str(exc.detail),
                "status": exc.status_code,
                "trace_id": _trace_id(request),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Error interno",
                "detail": "El motor de cotizacion no pudo procesar la solicitud.",
                "status": 500,
                "trace_id": _trace_id(request),
            },
        )

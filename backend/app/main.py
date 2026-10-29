from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from .config import settings
from .database import init_db
from .errors import NoEncontradoError, ReglaNegocioError
from .routers import agente, indicadores, productos, ventas


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="InsightDesk AI", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(NoEncontradoError)
async def _no_encontrado(_: Request, exc: NoEncontradoError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(ReglaNegocioError)
async def _regla_negocio(_: Request, exc: ReglaNegocioError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.get("/", include_in_schema=False)
def raiz():
    # La API no tiene página propia; se redirige a la documentación interactiva.
    return RedirectResponse(url="/docs")


@app.get("/api/health")
def health() -> dict:
    # Indica si el agente tiene clave configurada, sin revelarla.
    return {"status": "ok", "agent_configured": bool(settings.gemini_api_key)}


for r in (productos.router, ventas.router, indicadores.router, agente.router):
    app.include_router(r)

from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..agente.agente import Agente, AgenteError
from ..config import settings
from ..database import get_db
from ..schemas import RespuestaChat, SolicitudChat

router = APIRouter(prefix="/api/agente", tags=["agente"])


def get_agente(db: Session = Depends(get_db)) -> Callable[[], Agente]:
    """Devuelve un constructor perezoso: la falta de clave se informa recién
    después de validar la solicitud, para que una entrada inválida dé 422 y no 503."""

    def crear() -> Agente:
        if not settings.gemini_api_key:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "El agente no está configurado: define GEMINI_API_KEY en el entorno del backend.",
            )
        return Agente(db)

    return crear


@router.post("/chat", response_model=RespuestaChat)
def chat(solicitud: SolicitudChat, crear_agente: Callable[[], Agente] = Depends(get_agente)):
    agente = crear_agente()
    try:
        return agente.responder(solicitud.mensaje, solicitud.historial)
    except AgenteError as exc:
        raise HTTPException(exc.status_code, exc.mensaje) from exc

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..agente.agente import Agente, AgenteError
from ..config import settings
from ..database import get_db
from ..schemas import RespuestaChat, SolicitudChat

router = APIRouter(prefix="/api/agente", tags=["agente"])


def get_agente(db: Session = Depends(get_db)) -> Agente:
    if not settings.gemini_api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "El agente no está configurado: define GEMINI_API_KEY en el entorno del backend.",
        )
    return Agente(db)


@router.post("/chat", response_model=RespuestaChat)
def chat(solicitud: SolicitudChat, agente: Agente = Depends(get_agente)):
    try:
        return agente.responder(solicitud.mensaje, solicitud.historial)
    except AgenteError as exc:
        raise HTTPException(exc.status_code, exc.mensaje) from exc

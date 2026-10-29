from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Indicadores
from ..services.indicadores import calcular_indicadores

router = APIRouter(prefix="/api/indicadores", tags=["indicadores"])


@router.get("", response_model=Indicadores)
def obtener(db: Session = Depends(get_db)):
    return calcular_indicadores(db)

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import VentaCreate, VentaOut
from ..services import catalogo

router = APIRouter(prefix="/api/ventas", tags=["ventas"])


@router.get("", response_model=list[VentaOut])
def listar(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return catalogo.listar_ventas(db, limit, offset)


@router.post("", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear(datos: VentaCreate, db: Session = Depends(get_db)):
    return catalogo.crear_venta(db, datos)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ProductoCreate, ProductoOut
from ..services import catalogo

router = APIRouter(prefix="/api/productos", tags=["productos"])


@router.get("", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    return catalogo.listar_productos(db)


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoCreate, db: Session = Depends(get_db)):
    return catalogo.crear_producto(db, datos)

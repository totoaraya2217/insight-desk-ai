"""Operaciones sobre productos y ventas. Las reglas de negocio viven aquí, no en los routers."""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import NoEncontradoError, ReglaNegocioError
from ..models import Producto, Venta
from ..schemas import ProductoCreate, VentaCreate, VentaOut


def listar_productos(db: Session) -> list[Producto]:
    return list(db.scalars(select(Producto).order_by(Producto.nombre)))


def crear_producto(db: Session, datos: ProductoCreate) -> Producto:
    # lower() de SQLite solo cubre ASCII; se compara en Python para soportar tildes y ñ.
    clave = datos.nombre.casefold()
    if any(n.casefold() == clave for n in db.scalars(select(Producto.nombre))):
        raise ReglaNegocioError(f"Ya existe un producto llamado '{datos.nombre}'")
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def _venta_out(v: Venta) -> VentaOut:
    return VentaOut(
        id=v.id,
        producto_id=v.producto_id,
        producto_nombre=v.producto.nombre,
        cantidad=v.cantidad,
        precio_unitario=v.precio_unitario,
        total=round(v.cantidad * v.precio_unitario, 2),
        fecha=v.fecha,
    )


def listar_ventas(db: Session, limit: int = 100, offset: int = 0) -> list[VentaOut]:
    stmt = select(Venta).join(Venta.producto).order_by(Venta.fecha.desc(), Venta.id.desc()).limit(limit).offset(offset)
    return [_venta_out(v) for v in db.scalars(stmt)]


def crear_venta(db: Session, datos: VentaCreate) -> VentaOut:
    producto = db.get(Producto, datos.producto_id)
    if producto is None:
        raise NoEncontradoError(f"Producto {datos.producto_id} no encontrado")
    venta = Venta(
        producto_id=producto.id,
        cantidad=datos.cantidad,
        precio_unitario=producto.precio,
        fecha=datos.fecha or date.today(),
    )
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return _venta_out(venta)

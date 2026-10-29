"""Indicadores comerciales calculados en SQL sobre las ventas almacenadas.

Es la única fuente de cifras: el dashboard (Fase 3) y las herramientas del agente
(Fase 4) deben usar estas funciones para que siempre reporten los mismos números.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Producto, Venta
from ..schemas import Indicadores, VentasCategoria

_importe = Venta.cantidad * Venta.precio_unitario


def _dinero(valor) -> float:
    return round(float(valor or 0), 2)


def ventas_por_categoria(db: Session) -> list[VentasCategoria]:
    ingresos = func.sum(_importe).label("ingresos")
    stmt = (
        select(Producto.categoria, func.count(Venta.id), func.sum(Venta.cantidad), ingresos)
        .join(Venta.producto)
        .group_by(Producto.categoria)
        .order_by(ingresos.desc(), Producto.categoria)
    )
    return [
        VentasCategoria(categoria=cat, num_ventas=n, cantidad_vendida=int(cant), ingresos=_dinero(ing))
        for cat, n, cant, ing in db.execute(stmt)
    ]


def calcular_indicadores(db: Session) -> Indicadores:
    n, cantidad, ingresos = db.execute(
        select(func.count(Venta.id), func.coalesce(func.sum(Venta.cantidad), 0), func.coalesce(func.sum(_importe), 0.0))
    ).one()
    return Indicadores(
        hay_datos=n > 0,
        num_ventas=n,
        cantidad_vendida=int(cantidad),
        ingresos=_dinero(ingresos),
        ticket_promedio=_dinero(ingresos / n) if n else None,
        ventas_por_categoria=ventas_por_categoria(db),
    )

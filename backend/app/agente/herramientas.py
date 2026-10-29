"""Herramientas de solo lectura que el agente puede invocar.

Seguridad:
- El modelo solo PROPONE una llamada (nombre + argumentos); el backend decide si la ejecuta.
- Lista blanca de nombres: cualquier otro nombre se rechaza.
- Ninguna herramienta recibe texto libre ni SQL: no declaran parámetros y se rechaza
  cualquier argumento que el modelo intente enviar.
- Todas usan los servicios de indicadores (SQLAlchemy, solo SELECT): no modifican registros.
"""
from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from ..services import indicadores

_LIMITE_PRODUCTOS = 100


def _pct(parte: float, total: float) -> float | None:
    return round(100 * parte / total, 1) if total else None


def consultar_resumen_ventas(db: Session) -> dict:
    ind = indicadores.calcular_indicadores(db)
    primera, ultima = indicadores.rango_fechas(db)
    return {
        "hay_datos": ind.hay_datos,
        "num_ventas": ind.num_ventas,
        "cantidad_vendida": ind.cantidad_vendida,
        "ingresos": ind.ingresos,
        "ticket_promedio": ind.ticket_promedio,
        "fecha_primera_venta": primera,
        "fecha_ultima_venta": ultima,
        "nota": "Totales históricos de todas las ventas registradas; no admite filtrar por período.",
    }


def consultar_ventas_por_producto(db: Session) -> dict:
    productos = indicadores.ventas_por_producto(db)
    total = sum(p["ingresos"] for p in productos)
    for p in productos:
        p["participacion_ingresos_pct"] = _pct(p["ingresos"], total)
    return {
        "hay_datos": total > 0,
        "orden": "ingresos de mayor a menor; incluye productos sin ventas (ingresos 0)",
        "total_productos": len(productos),
        "truncado": len(productos) > _LIMITE_PRODUCTOS,
        "productos": productos[:_LIMITE_PRODUCTOS],
    }


def consultar_ventas_por_categoria(db: Session) -> dict:
    categorias = [c.model_dump() for c in indicadores.ventas_por_categoria(db)]
    total = sum(c["ingresos"] for c in categorias)
    for c in categorias:
        c["participacion_ingresos_pct"] = _pct(c["ingresos"], total)
        c["ticket_promedio"] = round(c["ingresos"] / c["num_ventas"], 2) if c["num_ventas"] else None
    return {"hay_datos": bool(categorias), "orden": "ingresos de mayor a menor", "categorias": categorias}


@dataclass(frozen=True)
class Herramienta:
    nombre: str
    descripcion: str
    ejecutar: Callable[[Session], dict]


HERRAMIENTAS: dict[str, Herramienta] = {
    h.nombre: h
    for h in (
        Herramienta(
            "consultar_resumen_ventas",
            "Totales históricos de ventas: número de ventas, unidades vendidas, ingresos, ticket promedio "
            "y rango de fechas con ventas registradas.",
            consultar_resumen_ventas,
        ),
        Herramienta(
            "consultar_ventas_por_producto",
            "Ventas de cada producto (unidades, ingresos, número de ventas, participación % en ingresos), "
            "ordenadas de mayor a menor ingreso. Incluye productos sin ventas. Úsala para alto y bajo rendimiento.",
            consultar_ventas_por_producto,
        ),
        Herramienta(
            "consultar_ventas_por_categoria",
            "Ventas por categoría de producto: unidades, ingresos, número de ventas, ticket promedio y "
            "participación % en ingresos.",
            consultar_ventas_por_categoria,
        ),
    )
}


def declaraciones() -> list[dict]:
    """Declaraciones de función para Gemini. Sin parámetros: nada de texto libre ni SQL."""
    return [{"name": h.nombre, "description": h.descripcion} for h in HERRAMIENTAS.values()]


def ejecutar_herramienta(db: Session, nombre: str, argumentos: dict | None) -> dict:
    """Ejecuta una herramienta de la lista blanca. Nunca lanza: los errores vuelven al modelo como datos."""
    herramienta = HERRAMIENTAS.get(nombre)
    if herramienta is None:
        return {"error": f"Herramienta no permitida: {nombre}"}
    if argumentos:
        return {"error": f"La herramienta {nombre} no acepta argumentos", "argumentos_rechazados": sorted(argumentos)}
    return herramienta.ejecutar(db)

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Categoria = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class _Entrada(BaseModel):
    # Campos desconocidos se rechazan (p. ej. un precio_unitario enviado por el cliente).
    model_config = ConfigDict(extra="forbid")


class ProductoCreate(_Entrada):
    nombre: Nombre
    categoria: Categoria
    precio: float = Field(gt=0, le=1_000_000_000)


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: str
    precio: float


class VentaCreate(_Entrada):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, le=10_000)
    fecha: date | None = Field(default=None, description="Por defecto, la fecha actual.")

    @field_validator("fecha")
    @classmethod
    def _no_futura(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("la fecha de venta no puede ser futura")
        return v


class VentaOut(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    total: float
    fecha: date


class VentasCategoria(BaseModel):
    categoria: str
    num_ventas: int
    cantidad_vendida: int
    ingresos: float


class Indicadores(BaseModel):
    hay_datos: bool
    num_ventas: int
    cantidad_vendida: int
    ingresos: float
    ticket_promedio: float | None = Field(description="Ingresos / número de ventas; null si no hay ventas.")
    ventas_por_categoria: list[VentasCategoria]

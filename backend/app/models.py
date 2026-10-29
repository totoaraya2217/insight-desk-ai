from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (CheckConstraint("precio > 0", name="ck_producto_precio_positivo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    categoria: Mapped[str] = mapped_column(String(60), index=True)
    precio: Mapped[float] = mapped_column(Float)

    ventas: Mapped[list["Venta"]] = relationship(back_populates="producto")


class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_venta_cantidad_positiva"),
        CheckConstraint("precio_unitario > 0", name="ck_venta_precio_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), index=True)
    cantidad: Mapped[int] = mapped_column(Integer)
    # Lo fija el backend con el precio del producto al momento de la venta.
    precio_unitario: Mapped[float] = mapped_column(Float)
    fecha: Mapped[date] = mapped_column(Date, index=True)

    producto: Mapped[Producto] = relationship(back_populates="ventas")

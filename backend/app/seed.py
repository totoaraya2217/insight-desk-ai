"""Datos de demostración reproducibles: `python -m app.seed` (agrega --reset para regenerar).

Semilla y fechas fijas: cada ejecución produce exactamente las mismas 50 ventas.
"""
import random
import sys
from datetime import date, timedelta

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, init_db
from .schemas import ProductoCreate, VentaCreate
from .services import catalogo

SEMILLA = 42
NUM_VENTAS = 50
FECHA_INICIO = date(2026, 1, 1)
DIAS = 181  # hasta 2026-06-30

PRODUCTOS = [
    ("Notebook Pro 14", "Computación", 899_990),
    ("Monitor 27 4K", "Computación", 329_990),
    ("Teclado mecánico", "Accesorios", 59_990),
    ("Mouse inalámbrico", "Accesorios", 19_990),
    ("Audífonos ANC", "Audio", 129_990),
    ("Parlante Bluetooth", "Audio", 49_990),
    ("Smartphone X12", "Telefonía", 549_990),
    ("Cargador USB-C 65W", "Telefonía", 24_990),
]


def poblar(db: Session) -> int:
    """Inserta productos y ventas en una base vacía. Devuelve la cantidad de ventas creadas."""
    if catalogo.listar_productos(db):
        return 0
    productos = [catalogo.crear_producto(db, ProductoCreate(nombre=n, categoria=c, precio=p)) for n, c, p in PRODUCTOS]
    rng = random.Random(SEMILLA)
    for _ in range(NUM_VENTAS):
        producto = rng.choice(productos)
        catalogo.crear_venta(
            db,
            VentaCreate(
                producto_id=producto.id,
                cantidad=rng.randint(1, 5),
                fecha=FECHA_INICIO + timedelta(days=rng.randrange(DIAS)),
            ),
        )
    return NUM_VENTAS


if __name__ == "__main__":
    if "--reset" in sys.argv:
        Base.metadata.drop_all(engine)
    init_db()
    with SessionLocal() as db:
        creadas = poblar(db)
    print(f"Creadas {creadas} ventas." if creadas else "La base ya tiene datos; usa --reset para regenerarla.")

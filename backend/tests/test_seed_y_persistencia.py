from datetime import date

from sqlalchemy import func, select

from app import seed
from app.database import crear_engine, crear_sessionmaker, init_db
from app.models import Producto, Venta
from app.schemas import ProductoCreate
from app.services import catalogo
from app.services.indicadores import calcular_indicadores


def _volcado(db):
    return [v.model_dump() for v in catalogo.listar_ventas(db, limit=500)]


def test_seed_crea_50_ventas(db):
    assert seed.poblar(db) == 50
    assert db.scalar(select(func.count(Venta.id))) == 50
    assert db.scalar(select(func.count(Producto.id))) == len(seed.PRODUCTOS)


def test_seed_es_reproducible(nueva_sesion):
    a, b = nueva_sesion(), nueva_sesion()
    seed.poblar(a)
    seed.poblar(b)
    assert _volcado(a) == _volcado(b)
    assert calcular_indicadores(a) == calcular_indicadores(b)


def test_seed_respeta_rangos_definidos(db):
    seed.poblar(db)
    precios = {n: p for n, _, p in seed.PRODUCTOS}
    for v in catalogo.listar_ventas(db, limit=500):
        assert date(2026, 1, 1) <= v.fecha <= date(2026, 6, 30)
        assert 1 <= v.cantidad <= 5
        assert v.precio_unitario == precios[v.producto_nombre]


def test_seed_no_duplica_si_ya_hay_datos(db):
    seed.poblar(db)
    assert seed.poblar(db) == 0
    assert db.scalar(select(func.count(Venta.id))) == 50


def test_indicadores_del_seed_coinciden_con_ventas(db):
    seed.poblar(db)
    ventas = catalogo.listar_ventas(db, limit=500)
    ind = calcular_indicadores(db)
    assert ind.num_ventas == 50
    assert ind.cantidad_vendida == sum(v.cantidad for v in ventas)
    assert ind.ingresos == round(sum(v.total for v in ventas), 2)
    assert ind.ticket_promedio == round(ind.ingresos / 50, 2)
    assert round(sum(c.ingresos for c in ind.ventas_por_categoria), 2) == ind.ingresos
    assert {c.categoria for c in ind.ventas_por_categoria} <= {c for _, c, _ in seed.PRODUCTOS}


def test_ventas_persisten_al_reiniciar(tmp_path):
    url = f"sqlite:///{(tmp_path / 'persistencia.db').as_posix()}"

    eng = crear_engine(url)
    init_db(eng)
    with crear_sessionmaker(eng)() as s:
        seed.poblar(s)
        esperado = _volcado(s)
    eng.dispose()  # simula apagar el servidor

    eng2 = crear_engine(url)
    with crear_sessionmaker(eng2)() as s:
        assert _volcado(s) == esperado
    eng2.dispose()


def test_clave_foranea_activa(db):
    import pytest
    from sqlalchemy.exc import IntegrityError

    catalogo.crear_producto(db, ProductoCreate(nombre="P", categoria="C", precio=1))
    db.add(Venta(producto_id=999, cantidad=1, precio_unitario=1, fecha=date(2026, 1, 1)))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

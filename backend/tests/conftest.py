import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.database import Base, crear_engine, crear_sessionmaker, get_db
from app.main import app


def _sesion_en_memoria():
    from app import models  # noqa: F401

    eng = crear_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng, crear_sessionmaker(eng)()


@pytest.fixture
def nueva_sesion():
    """Fábrica de sesiones sobre bases en memoria independientes."""
    creadas = []

    def _crear():
        eng, sesion = _sesion_en_memoria()
        creadas.append((eng, sesion))
        return sesion

    yield _crear
    for eng, sesion in creadas:
        sesion.close()
        eng.dispose()


@pytest.fixture
def db(nueva_sesion):
    return nueva_sesion()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def datos_conocidos(client):
    """3 productos (uno sin ventas) y 3 ventas con totales calculables a mano."""
    alfa = client.post("/api/productos", json={"nombre": "Alfa", "categoria": "X", "precio": 100}).json()
    beta = client.post("/api/productos", json={"nombre": "Beta", "categoria": "Y", "precio": 10.5}).json()
    gamma = client.post("/api/productos", json={"nombre": "Gamma", "categoria": "X", "precio": 5}).json()
    client.post("/api/ventas", json={"producto_id": alfa["id"], "cantidad": 2, "fecha": "2026-01-10"})
    client.post("/api/ventas", json={"producto_id": alfa["id"], "cantidad": 1, "fecha": "2026-02-05"})
    client.post("/api/ventas", json={"producto_id": beta["id"], "cantidad": 4, "fecha": "2026-02-20"})
    return {"alfa": alfa, "beta": beta, "gamma": gamma}

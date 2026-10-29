from datetime import date, timedelta


# --- Productos ---
def test_crear_y_listar_productos(client):
    r = client.post("/api/productos", json={"nombre": "  Teclado  ", "categoria": "Accesorios", "precio": 59990})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "nombre": "Teclado", "categoria": "Accesorios", "precio": 59990}
    assert client.get("/api/productos").json() == [r.json()]


def test_producto_validaciones(client):
    assert client.post("/api/productos", json={"nombre": "", "categoria": "C", "precio": 1}).status_code == 422
    assert client.post("/api/productos", json={"nombre": "A", "categoria": "C", "precio": 0}).status_code == 422
    assert client.post("/api/productos", json={"nombre": "A", "categoria": "C", "precio": -5}).status_code == 422
    assert client.post("/api/productos", json={"nombre": "A", "categoria": "C"}).status_code == 422
    assert client.post("/api/productos", json={"nombre": "A", "categoria": "C", "precio": 1, "id": 99}).status_code == 422


def test_producto_nombre_duplicado_sin_distinguir_mayusculas_ni_tildes(client):
    client.post("/api/productos", json={"nombre": "Único", "categoria": "C", "precio": 5})
    r = client.post("/api/productos", json={"nombre": "único", "categoria": "C", "precio": 5})
    assert r.status_code == 409


# --- Ventas ---
def test_venta_toma_precio_del_producto(client, datos_conocidos):
    r = client.post("/api/ventas", json={"producto_id": datos_conocidos["beta"]["id"], "cantidad": 3, "fecha": "2026-03-01"})
    assert r.status_code == 201
    venta = r.json()
    assert venta["precio_unitario"] == 10.5
    assert venta["total"] == 31.5
    assert venta["producto_nombre"] == "Beta"


def test_cliente_no_puede_fijar_precio(client, datos_conocidos):
    r = client.post("/api/ventas", json={"producto_id": datos_conocidos["alfa"]["id"], "cantidad": 1, "precio_unitario": 1})
    assert r.status_code == 422


def test_venta_validaciones(client, datos_conocidos):
    pid = datos_conocidos["alfa"]["id"]
    manana = (date.today() + timedelta(days=1)).isoformat()
    assert client.post("/api/ventas", json={"producto_id": pid, "cantidad": 0}).status_code == 422
    assert client.post("/api/ventas", json={"producto_id": pid, "cantidad": -1}).status_code == 422
    assert client.post("/api/ventas", json={"producto_id": pid, "cantidad": 1, "fecha": manana}).status_code == 422
    assert client.post("/api/ventas", json={"producto_id": pid, "cantidad": 1, "fecha": "no-es-fecha"}).status_code == 422
    assert client.post("/api/ventas", json={"producto_id": 999, "cantidad": 1}).status_code == 404


def test_venta_sin_fecha_usa_hoy(client, datos_conocidos):
    venta = client.post("/api/ventas", json={"producto_id": datos_conocidos["alfa"]["id"], "cantidad": 1}).json()
    assert venta["fecha"] == date.today().isoformat()


def test_listar_ventas_ordenadas_por_fecha_desc(client, datos_conocidos):
    ventas = client.get("/api/ventas").json()
    assert [v["fecha"] for v in ventas] == ["2026-02-20", "2026-02-05", "2026-01-10"]
    assert client.get("/api/ventas", params={"limit": 1}).json()[0]["fecha"] == "2026-02-20"
    assert client.get("/api/ventas", params={"limit": 0}).status_code == 422


def test_endpoints_responden_json(client, datos_conocidos):
    for ruta in ("/api/productos", "/api/ventas", "/api/indicadores", "/api/health"):
        r = client.get(ruta)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/json")
        r.json()

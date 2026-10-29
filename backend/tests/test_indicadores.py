def test_indicadores_con_datos_conocidos(client, datos_conocidos):
    ind = client.get("/api/indicadores").json()
    assert ind["hay_datos"] is True
    assert ind["num_ventas"] == 3
    assert ind["cantidad_vendida"] == 7  # 2 + 1 + 4
    assert ind["ingresos"] == 342.0  # 2*100 + 1*100 + 4*10.5
    assert ind["ticket_promedio"] == 114.0  # 342 / 3
    assert ind["ventas_por_categoria"] == [
        {"categoria": "X", "num_ventas": 2, "cantidad_vendida": 3, "ingresos": 300.0},
        {"categoria": "Y", "num_ventas": 1, "cantidad_vendida": 4, "ingresos": 42.0},
    ]


def test_indicadores_coinciden_con_ventas_almacenadas(client, datos_conocidos):
    ventas = client.get("/api/ventas").json()
    ind = client.get("/api/indicadores").json()
    assert ind["num_ventas"] == len(ventas)
    assert ind["cantidad_vendida"] == sum(v["cantidad"] for v in ventas)
    assert ind["ingresos"] == round(sum(v["total"] for v in ventas), 2)
    assert sum(c["ingresos"] for c in ind["ventas_por_categoria"]) == ind["ingresos"]


def test_indicadores_se_actualizan_al_registrar_venta(client, datos_conocidos):
    client.post("/api/ventas", json={"producto_id": datos_conocidos["gamma"]["id"], "cantidad": 2, "fecha": "2026-03-01"})
    ind = client.get("/api/indicadores").json()
    assert ind["ingresos"] == 352.0
    assert ind["ventas_por_categoria"][0] == {"categoria": "X", "num_ventas": 3, "cantidad_vendida": 5, "ingresos": 310.0}


def test_indicadores_sin_ventas_no_inventan_valores(client):
    client.post("/api/productos", json={"nombre": "Solo", "categoria": "Z", "precio": 10})
    ind = client.get("/api/indicadores").json()
    assert ind == {
        "hay_datos": False,
        "num_ventas": 0,
        "cantidad_vendida": 0,
        "ingresos": 0.0,
        "ticket_promedio": None,
        "ventas_por_categoria": [],
    }

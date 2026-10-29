"""Pruebas de humo de la Fase 1 (sin httpx: se prueba la app sin cliente HTTP)."""
import dataclasses

from app import main
from app.config import Settings


def test_app_registers_spec_routes():
    paths = main.app.openapi()["paths"]
    assert set(paths["/api/productos"]) == {"get", "post"}
    assert set(paths["/api/ventas"]) == {"get", "post"}
    assert set(paths["/api/indicadores"]) == {"get"}
    assert set(paths["/api/agente/chat"]) == {"post"}
    assert "/api/health" in paths


def test_health_reports_status_without_key(monkeypatch):
    monkeypatch.setattr(main, "settings", dataclasses.replace(main.settings, gemini_api_key=""))
    assert main.health() == {"status": "ok", "agent_configured": False}


def test_api_key_is_read_from_env_and_never_printed(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "SECRET-123")
    s = Settings()
    assert s.gemini_api_key == "SECRET-123"
    assert "SECRET-123" not in repr(s)


def test_cargar_env_lee_archivo_sin_pisar_entorno(tmp_path, monkeypatch):
    from app.config import cargar_env

    archivo = tmp_path / ".env"
    archivo.write_text('# comentario\nPRUEBA_A=uno\nPRUEBA_B = "dos"\nPRUEBA_C=desde_archivo\nPRUEBA_VACIA=\n', encoding="utf-8")
    for k in ("PRUEBA_A", "PRUEBA_B", "PRUEBA_VACIA"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("PRUEBA_C", "desde_entorno")

    cargar_env(archivo)
    import os

    assert os.environ["PRUEBA_A"] == "uno"
    assert os.environ["PRUEBA_B"] == "dos"
    assert os.environ["PRUEBA_C"] == "desde_entorno"
    assert "PRUEBA_VACIA" not in os.environ
    for k in ("PRUEBA_A", "PRUEBA_B"):
        monkeypatch.delenv(k)


def test_default_database_path_is_absolute(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    url = Settings().database_url
    assert url.startswith("sqlite:///") and url.endswith("backend/insightdesk.db")

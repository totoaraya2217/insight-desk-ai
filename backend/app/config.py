"""Configuración desde variables de entorno. Las claves nunca se escriben en el código."""
import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def cargar_env(ruta: Path) -> None:
    """Carga líneas CLAVE=valor de un archivo .env (sin dependencias externas).

    Las variables ya definidas en el entorno tienen prioridad y no se sobrescriben.
    """
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = (p.strip() for p in linea.split("=", 1))
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        if clave and valor and clave not in os.environ:
            os.environ[clave] = valor


cargar_env(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip(), repr=False)
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    gemini_timeout_s: float = field(default_factory=lambda: float(os.getenv("GEMINI_TIMEOUT_S", "30")))
    # Tope de rondas modelo→herramienta→modelo por pregunta (evita bucles y costos descontrolados).
    agente_max_pasos: int = 5
    # Ruta absoluta por defecto: la base persiste igual sin importar desde dónde se lance uvicorn.
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'insightdesk.db').as_posix()}")
    )
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)


settings = Settings()

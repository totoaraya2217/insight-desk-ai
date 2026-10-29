"""Configuración desde variables de entorno. Las claves nunca se escriben en el código."""
import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip(), repr=False)
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    # Ruta absoluta por defecto: la base persiste igual sin importar desde dónde se lance uvicorn.
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'insightdesk.db').as_posix()}")
    )
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)


settings = Settings()

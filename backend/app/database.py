from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


def crear_engine(url: str, **kwargs) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    eng = create_engine(url, connect_args=connect_args, **kwargs)

    if url.startswith("sqlite"):
        @event.listens_for(eng, "connect")
        def _activar_fk(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return eng


def crear_sessionmaker(eng: Engine) -> sessionmaker:
    return sessionmaker(bind=eng, autoflush=False, expire_on_commit=False)


engine = crear_engine(settings.database_url)
SessionLocal = crear_sessionmaker(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(eng: Engine = engine) -> None:
    from . import models  # noqa: F401  (registra las tablas en Base.metadata)

    Base.metadata.create_all(eng)

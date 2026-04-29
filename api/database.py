import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


def _make_engine():
    url = os.getenv('DATABASE_URL', 'sqlite:///./dev.db')
    if url == 'sqlite://':
        # In-memory SQLite para tests: StaticPool asegura que todas las
        # sesiones comparten la misma conexión (y la misma BD en memoria).
        from sqlalchemy.pool import StaticPool
        return create_engine(
            url,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
        )
    kwargs = {'check_same_thread': False} if url.startswith('sqlite') else {}
    return create_engine(url, connect_args=kwargs)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Dependency de FastAPI para inyectar la sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

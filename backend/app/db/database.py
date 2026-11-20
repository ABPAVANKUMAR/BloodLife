
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


Base = declarative_base()

engine = None
SessionLocal = None

if settings.DATABASE_URL:
    connect_args = {}

    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL in .env"
        )

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def create_tables():
    if engine is None:
        raise RuntimeError("Database engine is not configured")

    import app.models

    Base.metadata.create_all(bind=engine)

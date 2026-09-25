from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

#conexion a base de datos PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    )

#creacion de sesion individual para cada peticion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#clase base para heredar modelos de tablas
Base = declarative_base()

#Inyector de dependencia FastAPI para obtener sesion por peticion y cerrar al finalizar
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
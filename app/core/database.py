import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde el .env de la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

# URL de conexión a PostgreSQL desde variable de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada. Crea un archivo .env en la raíz del proyecto.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        # yield entrega la sesión al controlador y pausa esta función
        yield db
    finally:
        # Esto se ejecuta siempre al final del request HTTP
        db.close()
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde archivo .env
load_dotenv()

# URL de conexión a PostgreSQL desde variable de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
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
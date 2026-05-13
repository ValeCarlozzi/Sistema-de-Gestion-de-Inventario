from app.core.database import engine
from app.models.domain import Base

print("Inicio creacion de tablas")
Base.metadata.create_all(bind=engine)
print("Tablas creadas con exito")
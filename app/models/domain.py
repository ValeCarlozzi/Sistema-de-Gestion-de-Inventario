from sqlalchemy import Boolean, Column, Integer, String, Numeric, ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Relación bidireccional
    productos = relationship("Producto", back_populates="categoria")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nombre_completo = Column(String(150), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint('stock_actual >= 0', name='chk_stock_positivo'),
    )

    categoria = relationship("Categoria", back_populates="productos")
    movimientos = relationship("Movimiento", back_populates="producto")
    historiales = relationship("HistorialProducto", back_populates="producto", cascade="all, delete-orphan")

class TipoMovimiento(Base):
    __tablename__ = "tipomovimiento"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)

    movimiento = relationship("Movimiento", back_populates="tipomovimiento")

class Movimiento(Base):
    __tablename__ = "movimiento"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipomovimiento.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    motivo = Column(String(255), nullable=True)
    usuario = Column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint('cantidad > 0', name='chk_cantidad_positiva'),
    )

    producto = relationship("Producto", back_populates="movimientos")
    tipomovimiento = relationship("TipoMovimiento", back_populates="movimiento")



class HistorialProducto(Base):
    __tablename__ = "historial_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    valores_anteriores = Column(JSONB, nullable=True)
    valores_nuevos = Column(JSONB, nullable=True)
    fecha_cambio = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuario = Column(String(100), nullable=False)

    producto = relationship("Producto", back_populates="historiales")
import enum
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

# --- ENUM PARA EL ESTADO DEL PRODUCTO ---
class ProductStatusEnum(str, enum.Enum):
    activo = "activo"
    pausado = "pausado"
    sin_stock = "sin_stock"


# --- MODELO: CATEGORÍAS (CON JERARQUÍA RECURSIVA) ---
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    
    categoria_padre_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=True)

    # Relaciones de SQLAlchemy
    subcategorias = relationship("Categoria", backref="padre", remote_side=[id])
    productos = relationship("Producto", back_populates="categoria")


# --- MODELO: PRODUCTO PRINCIPAL ---
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)
    
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    precio_base = Column(Numeric(10, 2), nullable=False)
    sku_base = Column(String(100), unique=True, nullable=True)
    
    # --- CAMPO NUEVO PARA IMAGEN ---
    imagen_url = Column(String(255), nullable=True) 
    
    status = Column(Enum(ProductStatusEnum), default=ProductStatusEnum.activo, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    variantes = relationship("VarianteProducto", back_populates="producto", cascade="all, delete-orphan")


# --- MODELO: VARIANTES DEL PRODUCTO ---
class VarianteProducto(Base):
    __tablename__ = "producto_variantes"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    
    atributos = Column(String(255), nullable=False) 
    precio_adicional = Column(Numeric(10, 2), default=0.00)
    stock = Column(Integer, default=0, nullable=False)
    sku_variante = Column(String(100), unique=True, nullable=True)

    # Relaciones
    producto = relationship("Producto", back_populates="variantes")
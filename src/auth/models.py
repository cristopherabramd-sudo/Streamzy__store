import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config.database import Base

class RoleEnum(str, enum.Enum):
    proveedor = "proveedor"
    cliente = "cliente"
    admin = "admin"

class VendorStatusEnum(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.cliente)

    # Relación uno-a-uno con Proveedor
    proveedor_perfil = relationship("Proveedor", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    nombre_tienda = Column(String(100), unique=True, index=True, nullable=False)
    documento_fiscal = Column(String(50), nullable=False)
    telefono = Column(String(20), nullable=False)
    status = Column(Enum(VendorStatusEnum), nullable=False, default=VendorStatusEnum.pendiente)

    # Relaciones
    usuario = relationship("Usuario", back_populates="proveedor_perfil")

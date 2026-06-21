from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pendiente") # pendiente, pagado, enviado, entregado

    detalles = relationship("DetallePedido", back_populates="pedido")

class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    variante_id = Column(Integer, ForeignKey("producto_variantes.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False) # Guardamos el precio al momento de la venta

    pedido = relationship("Pedido", back_populates="detalles")
    variante = relationship("VarianteProducto")
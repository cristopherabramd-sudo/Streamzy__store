from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from config.database import get_db
from src.auth.dependencies import get_current_user  # Importación única y correcta
from src.orders.models import Pedido, DetallePedido
from src.products.models import VarianteProducto

router = APIRouter(prefix="/orders", tags=["Pedidos y Ventas"])

class ItemCarrito(BaseModel):
    variante_id: int
    cantidad: int

@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def realizar_pedido(items: List[ItemCarrito], db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        total_pedido = 0
        detalles = []

        # 1. Validar stock y calcular total
        for item in items:
            variante = db.query(VarianteProducto).filter(VarianteProducto.id == item.variante_id).first()
            if not variante or variante.stock < item.cantidad:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para la variante ID: {item.variante_id}")
            
            # Calcular precio (precio base + adicional)
            precio_item = variante.producto.precio_base + variante.precio_adicional
            total_pedido += (precio_item * item.cantidad)
            
            # Guardar datos para crear detalles después
            detalles.append({"variante": variante, "cantidad": item.cantidad, "precio": precio_item})
            
            # Descontar stock
            variante.stock -= item.cantidad

        # 2. Crear Pedido
        nuevo_pedido = Pedido(usuario_id=current_user.id, total=total_pedido, status="pagado")
        db.add(nuevo_pedido)
        db.flush() # Obtener ID del pedido

        # 3. Crear detalles
        for det in detalles:
            db.add(DetallePedido(
                pedido_id=nuevo_pedido.id,
                variante_id=det["variante"].id,
                cantidad=det["cantidad"],
                precio_unitario=det["precio"]
            ))

        db.commit()
        return {"message": "¡Pedido realizado con éxito!", "pedido_id": nuevo_pedido.id, "total": total_pedido}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/me", response_model=List[dict])
def listar_mis_pedidos(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Lista todos los pedidos realizados por el usuario autenticado."""
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == current_user.id).all()
    
    return [
        {
            "id": p.id,
            "total": p.total,
            "fecha": p.fecha_pedido,
            "status": p.status,
            "items_count": len(p.detalles)
        } for p in pedidos
    ]
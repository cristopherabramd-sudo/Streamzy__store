from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from config.database import get_db
from src.products.models import Categoria, Producto, VarianteProducto
from src.products.schemas import CategoriaCreate, CategoriaResponse, ProductoCreate, ProductoResponse
from src.auth.models import Proveedor
from src.auth.router import get_current_vendor

router = APIRouter(prefix="/products", tags=["Catálogo de Productos"])

# ==========================================
# 1. ENDPOINTS DE CATEGORÍAS
# ==========================================
@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(request: CategoriaCreate, db: Session = Depends(get_db)):
    if db.query(Categoria).filter(Categoria.nombre == request.nombre).first():
        raise HTTPException(status_code=400, detail="La categoría ya existe.")
    
    if request.categoria_padre_id:
        padre = db.query(Categoria).filter(Categoria.id == request.categoria_padre_id).first()
        if not padre:
            raise HTTPException(status_code=404, detail="La categoría padre especificada no existe.")

    nueva_categoria = Categoria(**request.model_dump())
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

# ==========================================
# 2. ENDPOINTS DE PRODUCTOS
# ==========================================
@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(
    request: ProductoCreate, 
    db: Session = Depends(get_db), 
    current_vendor: Proveedor = Depends(get_current_vendor)
):
    categoria = db.query(Categoria).filter(Categoria.id == request.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="La categoría seleccionada no existe.")

    if request.sku_base and db.query(Producto).filter(Producto.sku_base == request.sku_base).first():
        raise HTTPException(status_code=400, detail="El SKU base ya está registrado.")

    try:
        nuevo_producto = Producto(
            proveedor_id=current_vendor.id,
            categoria_id=request.categoria_id,
            titulo=request.titulo,
            descripcion=request.descripcion,
            precio_base=request.precio_base,
            sku_base=request.sku_base
        )
        db.add(nuevo_producto)
        db.flush() 

        for v in request.variantes:
            nueva_variante = VarianteProducto(
                producto_id=nuevo_producto.id,
                atributos=v.atributos,
                precio_adicional=v.precio_adicional,
                stock=v.stock,
                sku_variante=v.sku_variante
            )
            db.add(nueva_variante)

        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[ProductoResponse])
def listar_productos_publicos(db: Session = Depends(get_db)):
    """
    Lista productos activos optimizando la carga de variantes con joinedload.
    """
    return db.query(Producto).options(
        joinedload(Producto.variantes)
    ).filter(Producto.status == "activo").all()
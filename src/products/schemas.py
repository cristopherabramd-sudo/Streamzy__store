from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from src.products.models import ProductStatusEnum

# --- SCHEMAS DE CATEGORÍA ---
class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=100, example="Tecnología")
    descripcion: Optional[str] = Field(None, example="Teléfonos, laptops y accesorios electrónicos")
    categoria_padre_id: Optional[int] = Field(None, example=None)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


# --- SCHEMAS DE VARIANTES (Tallas, Colores, Almacenamiento) ---
class VarianteBase(BaseModel):
    atributos: str = Field(..., example="Color: Negro, Talla: L")
    precio_adicional: Decimal = Field(default=Decimal("0.00"), example=0.00)
    stock: int = Field(..., ge=0, example=15)
    sku_variante: Optional[str] = Field(None, example="FRA-NEG-L")

class VarianteCreate(VarianteBase):
    pass

class VarianteResponse(VarianteBase):
    id: int
    producto_id: int

    class Config:
        from_attributes = True


# --- SCHEMAS DE PRODUCTO ---
class ProductoCreate(BaseModel):
    categoria_id: int = Field(..., example=1)
    titulo: str = Field(..., max_length=255, example="Franela de Algodón Minimalista")
    descripcion: str = Field(..., example="Franela 100% algodón, ideal para uso diario.")
    precio_base: Decimal = Field(..., ge=0.01, example=15.99)
    sku_base: Optional[str] = Field(None, example="FRA-BASE-01")
    # Al crear el producto, permitimos meter de una vez sus variantes
    variantes: List[VarianteCreate] = Field(default=[], description="Lista de variantes iniciales")

class ProductoResponse(BaseModel):
    id: int
    proveedor_id: int
    categoria_id: int
    titulo: str
    descripcion: str
    precio_base: Decimal
    sku_base: Optional[str]
    status: ProductStatusEnum
    variantes: List[VarianteResponse] = []

    class Config:
        from_attributes = True
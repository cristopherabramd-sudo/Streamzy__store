from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.database import Base, engine

# Importación de Routers
from src.auth.router import router as auth_router
from src.products.router import router as products_router
from src.products.images import router as images_router
from src.orders.router import router as orders_router

# --- CONFIGURACIÓN DE BASE DE DATOS ---
# NOTA: En producción, esto debe reemplazarse por migraciones (Alembic)
# Comentamos drop_all para conservar los datos creados entre reinicios
# Base.metadata.drop_all(bind=engine) 
Base.metadata.create_all(bind=engine)

# --- FUNCIÓN PARA SEMBRAR DATOS DE PRUEBA (SEEDER) ---
def seed_database():
    from config.database import SessionLocal
    from src.auth.models import Usuario, Proveedor, RoleEnum, VendorStatusEnum
    from src.auth.utils import hash_password
    from src.products.models import Categoria, Producto, VarianteProducto
    
    db = SessionLocal()
    try:
        # Solo sembramos si la tabla de categorías está vacía
        if db.query(Categoria).first() is None:
            # 1. Crear Categorías
            cat_electronica = Categoria(nombre="Electrónica", descripcion="Artículos y gadgets electrónicos")
            cat_ropa = Categoria(nombre="Ropa", descripcion="Ropa y moda")
            db.add_all([cat_electronica, cat_ropa])
            db.flush()

            # 2. Crear Proveedor de prueba
            usuario_vendor = Usuario(
                nombre="Juan Proveedor",
                email="proveedor@streamzy.com",
                password_hash=hash_password("123456"),
                rol=RoleEnum.proveedor
            )
            db.add(usuario_vendor)
            db.flush()

            proveedor = Proveedor(
                usuario_id=usuario_vendor.id,
                nombre_tienda="STREAMZY STORE",
                documento_fiscal="RUT-12345678-9",
                telefono="+56912345678",
                status=VendorStatusEnum.aprobado
            )
            db.add(proveedor)
            db.flush()

            # 3. Crear Productos con sus Variantes
            prod_audifonos = Producto(
                proveedor_id=proveedor.id,
                categoria_id=cat_electronica.id,
                titulo="Audífonos Inalámbricos Bluetooth",
                descripcion="Audífonos con cancelación de ruido activa y batería de 40 horas.",
                precio_base=49.99,
                sku_base="AUD-BLU-001"
            )
            db.add(prod_audifonos)
            db.flush()

            variante_negro = VarianteProducto(
                producto_id=prod_audifonos.id,
                atributos="Color: Negro",
                precio_adicional=0.00,
                stock=15,
                sku_variante="AUD-BLU-001-N"
            )
            variante_blanco = VarianteProducto(
                producto_id=prod_audifonos.id,
                atributos="Color: Blanco",
                precio_adicional=5.00,
                stock=8,
                sku_variante="AUD-BLU-001-B"
            )
            db.add_all([variante_negro, variante_blanco])

            prod_polera = Producto(
                proveedor_id=proveedor.id,
                categoria_id=cat_ropa.id,
                titulo="Polera Deportiva Streamzy",
                descripcion="Polera deportiva transpirable de alta calidad.",
                precio_base=19.99,
                sku_base="POL-DEP-002"
            )
            db.add(prod_polera)
            db.flush()

            variante_m = VarianteProducto(
                producto_id=prod_polera.id,
                atributos="Talla: M",
                precio_adicional=0.00,
                stock=50,
                sku_variante="POL-DEP-002-M"
            )
            variante_l = VarianteProducto(
                producto_id=prod_polera.id,
                atributos="Talla: L",
                precio_adicional=2.00,
                stock=30,
                sku_variante="POL-DEP-002-L"
            )
            db.add_all([variante_m, variante_l])

            db.commit()
            print("Base de datos sembrada con datos de prueba.")
    except Exception as e:
        db.rollback()
        print(f"Error al sembrar la base de datos: {e}")
    finally:
        db.close()

seed_database()

app = FastAPI(title="Multi-Vendor Marketplace API", version="1.0")

# --- CONFIGURACIÓN DE FRONTEND ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Registro de rutas de la API
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(images_router)
app.include_router(orders_router)

# --- ENDPOINT DE VISTA PRINCIPAL ---
@app.get("/")
def home(request: Request):
    # Cambia esto:
    # return templates.TemplateResponse("index.html", {"request": request})
    
    # Por esto (especificando los argumentos explícitamente):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

@app.get("/health")
def health_check():
    return {"status": "Marketplace API Running", "database": "connected"}
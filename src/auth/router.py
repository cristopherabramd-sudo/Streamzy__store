import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from config.database import get_db
from src.auth.models import Usuario, Proveedor, RoleEnum, VendorStatusEnum
from src.auth.schemas import VendorRegisterRequest, TokenResponse
from src.auth.utils import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- ENDPOINT: REGISTRO AUTÓNOMO ---
@router.post("/register-vendor", status_code=status.HTTP_201_CREATED)
def register_vendor(request: VendorRegisterRequest, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == request.usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
        
    if db.query(Proveedor).filter(Proveedor.nombre_tienda == request.nombre_tienda).first():
        raise HTTPException(status_code=400, detail="El nombre de la tienda ya está en uso.")

    try:
        nuevo_usuario = Usuario(
            nombre=request.usuario.nombre,
            email=request.usuario.email,
            password_hash=hash_password(request.usuario.password),
            rol=RoleEnum.proveedor
        )
        db.add(nuevo_usuario)
        db.flush() 

        nuevo_proveedor = Proveedor(
            usuario_id=nuevo_usuario.id,
            nombre_tienda=request.nombre_tienda,
            documento_fiscal=request.documento_fiscal,
            telefono=request.telefono,
            status=VendorStatusEnum.pendiente
        )
        db.add(nuevo_proveedor)
        
        db.commit()
        return {"message": "Registro exitoso. Tu tienda está en espera de aprobación."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar el registro.")

# --- ENDPOINT: INICIO DE SESIÓN ---
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    
    rol_value = usuario.rol.value if hasattr(usuario.rol, 'value') else usuario.rol
    token = create_access_token(data={"sub": usuario.email, "id": usuario.id, "rol": rol_value})
    
    return {"access_token": token, "token_type": "bearer", "rol": rol_value}

# --- DEPENDENCY: PROTECCIÓN DE RUTAS ---
def get_current_vendor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Proveedor:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        rol = payload.get("rol")
        if not email or rol != RoleEnum.proveedor.value:
            raise Exception()
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o no autorizado.", headers={"WWW-Authenticate": "Bearer"})

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.proveedor_perfil:
        raise HTTPException(status_code=404, detail="Perfil de proveedor no encontrado.")
    
    if usuario.proveedor_perfil.status != VendorStatusEnum.aprobado:
        raise HTTPException(status_code=403, detail=f"Tu cuenta está en estado: {usuario.proveedor_perfil.status.value}.")
        
    return usuario.proveedor_perfil

# --- NUEVO ENDPOINT: OBTENER PERFIL (CONECTIVIDAD FRONTEND) ---
@router.get("/me")
def obtener_perfil(current_vendor: Proveedor = Depends(get_current_vendor)):
    """
    Endpoint para que el frontend obtenga los datos del proveedor logueado.
    """
    return {
        "usuario_id": current_vendor.usuario_id,
        "nombre": current_vendor.usuario.nombre,
        "email": current_vendor.usuario.email,
        "tienda": current_vendor.nombre_tienda,
        "status": current_vendor.status.value
    }

# --- ENDPOINT: APROBACIÓN RÁPIDA (PARA DEV) ---
@router.put("/aprobar-tienda-rapido")
def aprobar_tienda_rapido(nombre_tienda: str, db: Session = Depends(get_db)):
    tienda = db.query(Proveedor).filter(Proveedor.nombre_tienda == nombre_tienda).first()
    if not tienda:
        raise HTTPException(status_code=404, detail="Tienda no encontrada.")
    tienda.status = VendorStatusEnum.aprobado
    db.commit()
    return {"message": f"Tienda '{nombre_tienda}' aprobada."}
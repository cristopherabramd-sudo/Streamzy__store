import shutil
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from src.products.models import Producto

router = APIRouter(prefix="/products", tags=["Imágenes"])

# Creamos la carpeta si no existe
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/{producto_id}/upload-image")
def upload_image(producto_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Validar que el producto exista
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Guardar el archivo en el servidor
    # Usamos producto_id para que el nombre sea único y no se sobrescriban las fotos
    file_path = f"{UPLOAD_DIR}/{producto_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Guardar la ruta en la base de datos
    producto.imagen_url = file_path
    db.commit()
    
    return {"message": "Imagen subida exitosamente", "url": file_path}
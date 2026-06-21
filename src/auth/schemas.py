from pydantic import BaseModel, EmailStr

# Esquema para registrar la parte del usuario
class UsuarioRegister(BaseModel):
    nombre: str
    email: EmailStr
    password: str

# Esquema completo para el registro de un vendedor
class VendorRegisterRequest(BaseModel):
    usuario: UsuarioRegister
    nombre_tienda: str
    documento_fiscal: str
    telefono: str

# Lo que envía el usuario para loguearse
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Lo que el backend le responde si las credenciales son correctas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    rol: str
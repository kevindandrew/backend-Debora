from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema para crear usuario (Request)
class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str
    # Datos de persona
    nombres: str
    paterno: str
    materno: Optional[str] = None
    ci: str

# Schema para respuesta de Usuario
class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str
    fecha_creacion: datetime
    estado: bool
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None

    class Config:
        from_attributes = True  # Antes era orm_mode en Pydantic v1

# Schema para mensaje de creación exitosa
class UsuarioCreateResponse(BaseModel):
    id: int
    username: str
    mensaje: str

# Schema para actualización por el propio usuario
class UsuarioUpdateMe(BaseModel):
    password: Optional[str] = None
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None

# Schema para actualización por administrador
class UsuarioUpdateAdmin(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[bool] = None
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None
    ci: Optional[str] = None

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

    class Config:
        from_attributes = True  # Antes era orm_mode en Pydantic v1

# Schema para mensaje de creación exitosa
class UsuarioCreateResponse(BaseModel):
    id: int
    username: str
    mensaje: str

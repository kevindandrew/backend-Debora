from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema para respuesta de Usuario
class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str
    fecha_creacion: datetime
    estado: bool

    class Config:
        from_attributes = True  # Antes era orm_mode en Pydantic v1

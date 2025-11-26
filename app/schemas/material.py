from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SolicitudMaterialBase(BaseModel):
    descripcion_pedido: str

class SolicitudMaterialCreate(SolicitudMaterialBase):
    pass

class SolicitudMaterialUpdate(BaseModel):
    estado: str  # PENDIENTE, APROBADO, RECHAZADO

class SolicitudMaterialResponse(SolicitudMaterialBase):
    id: int
    unidad_id: int
    jefe_id: int
    fecha_solicitud: datetime
    estado: str
    
    class Config:
        from_attributes = True

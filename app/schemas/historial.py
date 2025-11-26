from pydantic import BaseModel
from typing import Optional
from datetime import date

class HistorialServicioBase(BaseModel):
    tipo_registro: str
    descripcion: str
    calificacion: Optional[int] = None

class HistorialServicioCreate(HistorialServicioBase):
    pass

class HistorialServicioResponse(HistorialServicioBase):
    id: int
    postulacion_id: int
    jefe_unidad_id: int
    fecha_registro: date
    
    class Config:
        from_attributes = True

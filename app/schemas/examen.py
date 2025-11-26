from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExamenAdicionalBase(BaseModel):
    tipo_examen: str
    resultado: str
    fecha_entrega: date

class ExamenAdicionalCreate(ExamenAdicionalBase):
    pass

class ExamenAdicionalResponse(ExamenAdicionalBase):
    id: int
    postulacion_id: int
    archivo_adjunto: Optional[str] = None
    
    class Config:
        from_attributes = True

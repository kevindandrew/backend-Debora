from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============================================
# SCHEMAS PARA TRÁMITES
# ============================================

class TramiteCreate(BaseModel):
    tipo_tramite: str = Field(..., description="RECTIFICACION, PERDIDA, CERTIFICACION")
    descripcion: str = Field(..., min_length=10, description="Descripción del trámite solicitado")

class TramiteResponse(BaseModel):
    tramite_id: int
    estado: str
    mensaje: str

class TramiteDetalle(BaseModel):
    id: int
    licenciado_usuario_id: int
    tipo: str
    descripcion_solicitud: str
    fecha_solicitud: datetime
    estado: str
    respuesta_admin: Optional[str]
    archivo_respuesta_url: Optional[str]
    
    class Config:
        from_attributes = True

class TramiteListItem(BaseModel):
    id: int
    tipo: str
    descripcion_solicitud: str
    estado: str
    fecha_solicitud: datetime
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA REQUISITOS DE TRÁMITE
# ============================================

class RequisitoUploadResponse(BaseModel):
    id: int
    mensaje: str

class RequisitoDetalle(BaseModel):
    id: int
    tramite_id: int
    nombre_requisito: str
    url_archivo: str
    validado: bool
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA RESPUESTA DE TRÁMITE
# ============================================

class TramiteRespuestaRequest(BaseModel):
    estado: str = Field(..., description="ACEPTADO o RECHAZADO")
    respuesta_texto: str = Field(..., min_length=10, description="Respuesta del administrador")

class TramiteRespuestaResponse(BaseModel):
    mensaje: str

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime

# ============================================
# SCHEMAS PARA TUTORES
# ============================================

class TutorCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=150)
    ci: str = Field(..., min_length=5, max_length=20)
    relacion: str = Field(..., description="Padre, Madre, Apoderado, etc.")

class TutorResponse(BaseModel):
    id: int
    nombre_completo: str
    ci: str
    relacion: str
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA POSTULACIONES
# ============================================

class PostulacionCreate(BaseModel):
    # Datos de la persona
    ci: str = Field(..., min_length=5, max_length=20)
    nombres: str = Field(..., min_length=2, max_length=100)
    paterno: str = Field(..., min_length=2, max_length=50)
    materno: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: date
    genero: str = Field(..., pattern="^[MF]$", description="M o F")
    direccion: Optional[str] = None
    
    # Datos de la postulación
    modalidad_id: int
    unidad_id: int
    
    # Tutor (opcional, se requiere si es menor de edad)
    tutor: Optional[TutorCreate] = None
    
    @field_validator('genero')
    @classmethod
    def validate_genero(cls, v):
        if v not in ['M', 'F']:
            raise ValueError('El género debe ser M o F')
        return v

class PostulacionResponse(BaseModel):
    codigo_inscripcion: str
    estado: str
    mensaje: str

class PostulacionListItem(BaseModel):
    codigo_inscripcion: str
    nombre_completo: str
    ci: str
    estado: str
    modalidad: str
    unidad: str
    fecha_postulacion: datetime
    
    class Config:
        from_attributes = True

class PostulacionDetalle(BaseModel):
    id: int
    codigo_inscripcion: str
    persona_id: int
    tutor_id: Optional[int]
    unidad_id: int
    modalidad_id: int
    gestion: int
    estado: str
    fecha_postulacion: datetime
    
    # Datos relacionados
    persona: dict
    tutor: Optional[dict] = None
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA DOCUMENTOS
# ============================================

class DocumentoUploadResponse(BaseModel):
    id: int
    url: str
    mensaje: str

class DocumentoResponse(BaseModel):
    id: int
    postulacion_id: int
    tipo_documento: str
    url_archivo: str
    fecha_subida: datetime
    
    class Config:
        from_attributes = True

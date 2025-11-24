from pydantic import BaseModel
from typing import Optional
from datetime import date

# ============================================
# SCHEMAS PARA UNIDADES DE RECLUTAMIENTO
# ============================================

class UnidadCreate(BaseModel):
    nombre: str
    departamento: str
    provincia: Optional[str] = None
    direccion_fisica: Optional[str] = None
    capacidad_maxima: int = 100
    jefe_unidad_id: Optional[int] = None

class UnidadResponse(BaseModel):
    id: int
    nombre: str
    departamento: str
    provincia: Optional[str]
    direccion_fisica: Optional[str]
    capacidad_maxima: int
    jefe_unidad_id: Optional[int]
    
    class Config:
        from_attributes = True

class UnidadCreateResponse(BaseModel):
    id: int
    nombre: str
    estado: str

# ============================================
# SCHEMAS PARA MODALIDADES
# ============================================

class ModalidadUpdate(BaseModel):
    fecha_inicio_inscripcion: Optional[date] = None
    fecha_fin_inscripcion: Optional[date] = None

class ModalidadResponse(BaseModel):
    id: int
    nombre: str
    edad_minima: int
    edad_maxima: int
    fecha_inicio_inscripcion: Optional[date]
    fecha_fin_inscripcion: Optional[date]
    descripcion: Optional[str]
    
    class Config:
        from_attributes = True

class ModalidadUpdateResponse(BaseModel):
    modalidad: str
    mensaje: str

# ============================================
# SCHEMAS PARA PERSONAL ASIGNADO
# ============================================

class PersonalAsignadoCreate(BaseModel):
    usuario_id: int
    rol_en_unidad: str  # MEDICO o SUPERVISOR
    gestion: int

class PersonalAsignadoResponse(BaseModel):
    id: int
    unidad_id: int
    usuario_id: int
    rol_en_unidad: str
    gestion: int
    
    class Config:
        from_attributes = True

class PersonalAsignadoCreateResponse(BaseModel):
    mensaje: str

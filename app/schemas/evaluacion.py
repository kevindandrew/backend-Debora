from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

# ============================================
# SCHEMAS PARA EVALUACIÓN MÉDICA
# ============================================

class EvaluacionMedicaCreate(BaseModel):
    postulacion_id: int
    peso: float = Field(..., gt=0, description="Peso en kg")
    estatura: float = Field(..., gt=0, description="Estatura en metros")
    grupo_sanguineo: str = Field(..., max_length=5, description="Ej: O+, A-, AB+")
    color_piel: Optional[str] = Field(None, max_length=30)
    color_ojos: Optional[str] = Field(None, max_length=30)
    tipo_nariz: Optional[str] = Field(None, max_length=30)
    tipo_boca: Optional[str] = Field(None, max_length=30)
    prueba_embarazo: Optional[bool] = Field(None, description="Solo para mujeres")
    observaciones: Optional[str] = None
    resultado_apto: bool = Field(..., description="¿Es apto médicamente?")

class EvaluacionMedicaResponse(BaseModel):
    id: int
    estado: str
    siguiente_paso: str

class EvaluacionMedicaDetalle(BaseModel):
    id: int
    postulacion_id: int
    medico_id: int
    peso: float
    estatura: float
    grupo_sanguineo: str
    color_piel: Optional[str]
    color_ojos: Optional[str]
    tipo_nariz: Optional[str]
    tipo_boca: Optional[str]
    prueba_embarazo: Optional[bool]
    observaciones: Optional[str]
    resultado_apto: bool
    fecha_evaluacion: date
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA EVALUACIÓN FÍSICA/SUPERVISIÓN
# ============================================

class EvaluacionFisicaCreate(BaseModel):
    postulacion_id: int
    flexiones: int = Field(..., ge=0, description="Número de flexiones")
    abdominales: int = Field(..., ge=0, description="Número de abdominales")
    carrera_3200m: str = Field(..., description="Tiempo en formato MM:SS o HH:MM:SS")
    sabe_leer: bool
    sabe_escribir: bool
    sabe_conducir: Optional[bool] = False
    resultado_psicologico: Optional[str] = Field(None, max_length=50)
    resultado_final_supervisor: bool = Field(..., description="¿Aprueba la evaluación física?")

class EvaluacionFisicaResponse(BaseModel):
    id: int
    mensaje: str

class EvaluacionFisicaDetalle(BaseModel):
    id: int
    postulacion_id: int
    supervisor_id: int
    flexiones: int
    abdominales: int
    carrera_3200m: time
    sabe_leer: bool
    sabe_escribir: bool
    sabe_conducir: Optional[bool]
    resultado_psicologico: Optional[str]
    resultado_final_supervisor: bool
    fecha_evaluacion: date
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA VEREDICTO FINAL
# ============================================

class VeredictoRequest(BaseModel):
    estado_final: str = Field(..., description="APTO o NO_APTO")
    comentario: Optional[str] = None

class VeredictoResponse(BaseModel):
    nuevo_estado: str
    mensaje: str

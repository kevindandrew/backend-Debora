from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EvaluacionSupervision(Base):
    __tablename__ = "evaluaciones_supervision"
    
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    supervisor_id = Column(Integer, ForeignKey("usuarios.id"))
    flexiones = Column(Integer)
    abdominales = Column(Integer)
    carrera_3200m = Column(Time)  # Tiempo en la carrera
    sabe_leer = Column(Boolean)
    sabe_escribir = Column(Boolean)
    sabe_conducir = Column(Boolean)
    resultado_psicologico = Column(String(50))
    resultado_final_supervisor = Column(Boolean)  # Apto / No Apto
    fecha_evaluacion = Column(Date, server_default=func.current_date())
    
    # Relaciones
    postulacion = relationship("Postulacion", back_populates="evaluacion_supervision")
    supervisor = relationship("Usuario", back_populates="evaluaciones_supervision")

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EvaluacionMedica(Base):
    __tablename__ = "evaluaciones_medicas"
    
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    medico_id = Column(Integer, ForeignKey("usuarios.id"))
    peso = Column(Numeric(5, 2))
    estatura = Column(Numeric(5, 2))
    grupo_sanguineo = Column(String(5))
    color_piel = Column(String(30))
    color_ojos = Column(String(30))
    tipo_nariz = Column(String(30))
    tipo_boca = Column(String(30))
    prueba_embarazo = Column(Boolean)  # Solo mujeres
    observaciones = Column(String)
    resultado_apto = Column(Boolean)
    fecha_evaluacion = Column(Date, server_default=func.current_date())
    
    # Relaciones
    postulacion = relationship("Postulacion", back_populates="evaluacion_medica")
    medico = relationship("Usuario", back_populates="evaluaciones_medicas")

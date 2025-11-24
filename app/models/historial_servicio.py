from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class HistorialServicio(Base):
    __tablename__ = "historial_servicio"
    
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    jefe_unidad_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_registro = Column(Date, server_default=func.current_date())
    tipo_registro = Column(String(50))  # Asistencia, Uniforme, Comportamiento
    descripcion = Column(String)
    calificacion = Column(Integer)  # Opcional, para evaluar desempeño
    
    # Relaciones
    postulacion = relationship("Postulacion", back_populates="historial_servicio")
    jefe_unidad = relationship("Usuario", back_populates="historial_registros")

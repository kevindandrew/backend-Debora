from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class ExamenAdicional(Base):
    __tablename__ = "examenes_adicionales"
    
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    tipo_examen = Column(String(50))  # ECG, EEG, RX Torax
    resultado = Column(String)
    archivo_adjunto = Column(String(255))
    fecha_entrega = Column(Date)
    
    # Relaciones
    postulacion = relationship("Postulacion", back_populates="examenes_adicionales")

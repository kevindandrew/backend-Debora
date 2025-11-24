from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Modalidad(Base):
    __tablename__ = "modalidades"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)  # Premilitar, Militar, Voluntariado
    edad_minima = Column(Integer, nullable=False)
    edad_maxima = Column(Integer, nullable=False)
    fecha_inicio_inscripcion = Column(Date)  # RF15
    fecha_fin_inscripcion = Column(Date)      # RF15
    descripcion = Column(String)
    
    # Relaciones
    postulaciones = relationship("Postulacion", back_populates="modalidad")

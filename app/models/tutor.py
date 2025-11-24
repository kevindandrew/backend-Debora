from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Tutor(Base):
    __tablename__ = "tutores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    ci = Column(String(20), nullable=False)
    relacion = Column(String(50))  # Padre, Madre, Apoderado
    
    # Relaciones
    postulaciones = relationship("Postulacion", back_populates="tutor")

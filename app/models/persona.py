from sqlalchemy import Column, Integer, String, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    paterno = Column(String(50), nullable=False, index=True)
    materno = Column(String(50))
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(1), nullable=False)  # 'M' o 'F'
    direccion = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="personas")
    postulaciones = relationship("Postulacion", back_populates="persona")

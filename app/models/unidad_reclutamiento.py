from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UnidadReclutamiento(Base):
    __tablename__ = "unidades_reclutamiento"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    departamento = Column(String(50), nullable=False)
    provincia = Column(String(50))
    direccion_fisica = Column(String)
    capacidad_maxima = Column(Integer, default=0)
    jefe_unidad_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relaciones
    jefe_unidad = relationship("Usuario", back_populates="unidades_jefe")
    solicitudes_material = relationship("SolicitudMaterial", back_populates="unidad")
    postulaciones = relationship("Postulacion", back_populates="unidad")
    personal_asignado = relationship("PersonalAsignado", back_populates="unidad")

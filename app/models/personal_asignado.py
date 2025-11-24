from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.usuario import RolUsuario

class PersonalAsignado(Base):
    __tablename__ = "personal_asignado"
    
    id = Column(Integer, primary_key=True, index=True)
    unidad_id = Column(Integer, ForeignKey("unidades_reclutamiento.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    rol_en_unidad = Column(Enum(RolUsuario, name="rol_usuario", create_type=False))  # MEDICO o SUPERVISOR
    gestion = Column(Integer, nullable=False)
    
    # Relaciones
    unidad = relationship("UnidadReclutamiento", back_populates="personal_asignado")
    usuario = relationship("Usuario", back_populates="personal_asignaciones")

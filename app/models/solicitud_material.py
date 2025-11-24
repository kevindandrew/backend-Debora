from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SolicitudMaterial(Base):
    __tablename__ = "solicitudes_material"
    
    id = Column(Integer, primary_key=True, index=True)
    unidad_id = Column(Integer, ForeignKey("unidades_reclutamiento.id"))
    jefe_id = Column(Integer, ForeignKey("usuarios.id"))
    descripcion_pedido = Column(String, nullable=False)
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(String(20), default="PENDIENTE")  # PENDIENTE, APROBADO, RECHAZADO
    
    # Relaciones
    unidad = relationship("UnidadReclutamiento", back_populates="solicitudes_material")
    jefe = relationship("Usuario", back_populates="solicitudes_material")

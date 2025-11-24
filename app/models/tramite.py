from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

# Enums para trámites
class TipoTramite(str, enum.Enum):
    RECTIFICACION = "RECTIFICACION"
    PERDIDA = "PERDIDA"
    CERTIFICACION = "CERTIFICACION"

class EstadoTramite(str, enum.Enum):
    SOLICITADO = "SOLICITADO"
    EN_REVISION = "EN_REVISION"
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"

class Tramite(Base):
    __tablename__ = "tramites"
    
    id = Column(Integer, primary_key=True, index=True)
    licenciado_usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(Enum(TipoTramite, name="tipo_tramite", create_type=False), nullable=False)
    descripcion_solicitud = Column(String)
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(Enum(EstadoTramite, name="estado_tramite", create_type=False), default=EstadoTramite.SOLICITADO)
    respuesta_admin = Column(String)
    archivo_respuesta_url = Column(String(255))  # PDF generado por admin
    
    # Relaciones
    licenciado_usuario = relationship("Usuario", back_populates="tramites")
    requisitos = relationship("RequisitoTramite", back_populates="tramite")

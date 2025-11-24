from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

# Enum para roles de usuario
class RolUsuario(str, enum.Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    DIRECTOR = "DIRECTOR"
    JEFE_UNIDAD = "JEFE_UNIDAD"
    MEDICO = "MEDICO"
    SUPERVISOR = "SUPERVISOR"
    LICENCIADO = "LICENCIADO"

# Modelo de Usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario, name="rol_usuario", create_type=False), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(Boolean, default=True)
    
    # Relaciones
    personas = relationship("Persona", back_populates="usuario")
    unidades_jefe = relationship("UnidadReclutamiento", back_populates="jefe_unidad")
    solicitudes_material = relationship("SolicitudMaterial", back_populates="jefe")
    personal_asignaciones = relationship("PersonalAsignado", back_populates="usuario")
    evaluaciones_medicas = relationship("EvaluacionMedica", back_populates="medico")
    evaluaciones_supervision = relationship("EvaluacionSupervision", back_populates="supervisor")
    documentos_subidos = relationship("DocumentoPostulante", back_populates="usuario_subida")
    historial_registros = relationship("HistorialServicio", back_populates="jefe_unidad")
    tramites = relationship("Tramite", back_populates="licenciado_usuario")

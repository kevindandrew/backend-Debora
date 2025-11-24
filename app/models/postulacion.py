from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

# Enum para estado de postulación
class EstadoPostulacion(str, enum.Enum):
    INSCRITO = "INSCRITO"
    EN_EVALUACION = "EN_EVALUACION"
    APTO = "APTO"
    NO_APTO = "NO_APTO"
    LICENCIADO = "LICENCIADO"
    BAJA = "BAJA"

class Postulacion(Base):
    __tablename__ = "postulaciones"
    __table_args__ = (
        UniqueConstraint('persona_id', 'gestion', name='uq_persona_gestion'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_inscripcion = Column(String(50), unique=True, nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"))
    tutor_id = Column(Integer, ForeignKey("tutores.id"))
    unidad_id = Column(Integer, ForeignKey("unidades_reclutamiento.id"))
    modalidad_id = Column(Integer, ForeignKey("modalidades.id"))
    gestion = Column(Integer, nullable=False)  # Año
    estado = Column(Enum(EstadoPostulacion, name="estado_postulacion", create_type=False), default=EstadoPostulacion.INSCRITO)
    fecha_postulacion = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    persona = relationship("Persona", back_populates="postulaciones")
    tutor = relationship("Tutor", back_populates="postulaciones")
    unidad = relationship("UnidadReclutamiento", back_populates="postulaciones")
    modalidad = relationship("Modalidad", back_populates="postulaciones")
    documentos = relationship("DocumentoPostulante", back_populates="postulacion")
    evaluacion_medica = relationship("EvaluacionMedica", back_populates="postulacion", uselist=False)
    evaluacion_supervision = relationship("EvaluacionSupervision", back_populates="postulacion", uselist=False)
    examenes_adicionales = relationship("ExamenAdicional", back_populates="postulacion")
    historial_servicio = relationship("HistorialServicio", back_populates="postulacion")

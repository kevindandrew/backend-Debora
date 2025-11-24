from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class DocumentoPostulante(Base):
    __tablename__ = "documentos_postulante"
    
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    tipo_documento = Column(String(50))  # Certificado Nacimiento, CI, etc.
    url_archivo = Column(String(255), nullable=False)
    subido_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_subida = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    postulacion = relationship("Postulacion", back_populates="documentos")
    usuario_subida = relationship("Usuario", back_populates="documentos_subidos")

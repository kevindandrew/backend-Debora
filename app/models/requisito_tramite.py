from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class RequisitoTramite(Base):
    __tablename__ = "requisitos_tramite"
    
    id = Column(Integer, primary_key=True, index=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"))
    nombre_requisito = Column(String(100))  # Ej: Boleta Depósito, Foto 4x4
    url_archivo = Column(String(255))
    validado = Column(Boolean, default=False)
    
    # Relaciones
    tramite = relationship("Tramite", back_populates="requisitos")

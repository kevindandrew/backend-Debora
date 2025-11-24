from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.modalidad import Modalidad
from app.models.usuario import Usuario
from app.schemas.modulo2 import ModalidadUpdate, ModalidadResponse, ModalidadUpdateResponse
from app.dependencies import require_role

router = APIRouter(
    prefix="/api/v1/modalidades",
    tags=["Modalidades"]
)

@router.get("/", response_model=List[ModalidadResponse])
def listar_modalidades(
    db: Session = Depends(get_db)
):
    """
    **Listar todas las modalidades**
    
    Muestra todas las modalidades disponibles (Premilitar, Militar, Voluntariado, etc.)
    con sus rangos de edad y fechas de inscripción.
    
    No requiere autenticación.
    """
    modalidades = db.query(Modalidad).all()
    return modalidades

@router.get("/{modalidad_id}", response_model=ModalidadResponse)
def obtener_modalidad(
    modalidad_id: int,
    db: Session = Depends(get_db)
):
    """
    **Obtener una modalidad específica**
    
    - **modalidad_id**: ID de la modalidad
    """
    modalidad = db.query(Modalidad).filter(Modalidad.id == modalidad_id).first()
    if not modalidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modalidad con ID {modalidad_id} no encontrada"
        )
    return modalidad

@router.patch("/{modalidad_id}", response_model=ModalidadUpdateResponse)
def configurar_fechas_modalidad(
    modalidad_id: int,
    modalidad_data: ModalidadUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Configurar Fechas y Modalidades (RF15)**
    
    Actualiza las fechas de inscripción para una modalidad específica.
    
    Requiere rol: ADMINISTRADOR o DIRECTOR
    
    - **fecha_inicio_inscripcion**: Fecha de inicio de inscripciones (formato: YYYY-MM-DD)
    - **fecha_fin_inscripcion**: Fecha de fin de inscripciones (formato: YYYY-MM-DD)
    """
    
    # Buscar modalidad
    modalidad = db.query(Modalidad).filter(Modalidad.id == modalidad_id).first()
    if not modalidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modalidad con ID {modalidad_id} no encontrada"
        )
    
    # Validar que las fechas tengan sentido
    if (modalidad_data.fecha_inicio_inscripcion and 
        modalidad_data.fecha_fin_inscripcion and
        modalidad_data.fecha_inicio_inscripcion > modalidad_data.fecha_fin_inscripcion):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio no puede ser posterior a la fecha de fin"
        )
    
    # Actualizar fechas
    if modalidad_data.fecha_inicio_inscripcion is not None:
        modalidad.fecha_inicio_inscripcion = modalidad_data.fecha_inicio_inscripcion
    
    if modalidad_data.fecha_fin_inscripcion is not None:
        modalidad.fecha_fin_inscripcion = modalidad_data.fecha_fin_inscripcion
    
    db.commit()
    db.refresh(modalidad)
    
    return ModalidadUpdateResponse(
        modalidad=modalidad.nombre,
        mensaje="Fechas actualizadas"
    )

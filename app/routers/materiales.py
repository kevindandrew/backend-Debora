from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.solicitud_material import SolicitudMaterial
from app.models.usuario import Usuario, RolUsuario
from app.models.unidad_reclutamiento import UnidadReclutamiento
from app.schemas.material import (
    SolicitudMaterialCreate,
    SolicitudMaterialResponse,
    SolicitudMaterialUpdate
)
from app.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/api/v1/materiales",
    tags=["Gestión de Materiales"]
)

@router.post("/solicitar", response_model=SolicitudMaterialResponse)
def solicitar_material(
    solicitud_data: SolicitudMaterialCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["JEFE_UNIDAD"]))
):
    """
    **Solicitar Material de Apoyo (RF11)**
    
    Permite a un Jefe de Unidad solicitar material.
    """
    # 1. Obtener la unidad del jefe
    unidad = db.query(UnidadReclutamiento).filter(
        UnidadReclutamiento.jefe_unidad_id == current_user.id
    ).first()
    
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene una unidad asignada como jefe"
        )
    
    # 2. Crear solicitud
    nueva_solicitud = SolicitudMaterial(
        unidad_id=unidad.id,
        jefe_id=current_user.id,
        descripcion_pedido=solicitud_data.descripcion_pedido,
        estado="PENDIENTE"
    )
    
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)
    
    return nueva_solicitud

@router.get("/", response_model=List[SolicitudMaterialResponse])
def listar_solicitudes(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "JEFE_UNIDAD", "DIRECTOR"]))
):
    """
    **Listar Solicitudes de Material (RF12)**
    
    - **ADMINISTRADOR/DIRECTOR**: Ven todas las solicitudes.
    - **JEFE_UNIDAD**: Ve solo sus propias solicitudes.
    """
    query = db.query(SolicitudMaterial)
    
    # Filtro por rol
    if current_user.rol == RolUsuario.JEFE_UNIDAD:
        query = query.filter(SolicitudMaterial.jefe_id == current_user.id)
    
    # Filtro opcional por estado
    if estado:
        query = query.filter(SolicitudMaterial.estado == estado)
        
    return query.all()

@router.patch("/{id}/estado", response_model=SolicitudMaterialResponse)
def actualizar_estado_solicitud(
    id: int,
    estado_data: SolicitudMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Aprobar/Rechazar Solicitud (RF12)**
    
    Permite a un Administrador o Director cambiar el estado de una solicitud.
    """
    solicitud = db.query(SolicitudMaterial).filter(SolicitudMaterial.id == id).first()
    
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud con ID {id} no encontrada"
        )
        
    if estado_data.estado not in ["PENDIENTE", "APROBADO", "RECHAZADO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use: PENDIENTE, APROBADO, RECHAZADO"
        )
        
    solicitud.estado = estado_data.estado
    db.commit()
    db.refresh(solicitud)
    
    return solicitud

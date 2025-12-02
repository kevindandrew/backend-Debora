from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.unidad_reclutamiento import UnidadReclutamiento
from app.models.usuario import Usuario, RolUsuario
from app.models.personal_asignado import PersonalAsignado
from app.schemas.modulo2 import (
    UnidadCreate, 
    UnidadResponse, 
    UnidadCreateResponse,
    PersonalAsignadoCreate,
    PersonalAsignadoCreateResponse,
    PersonalInfo
)
from app.dependencies import require_role

router = APIRouter(
    prefix="/api/v1/unidades",
    tags=["Unidades de Reclutamiento"]
)

@router.post("/", response_model=UnidadCreateResponse)
def crear_unidad(
    unidad_data: UnidadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Crear Unidad de Reclutamiento (RF10)**
    
    Crea un nuevo centro de reclutamiento.
    
    Requiere rol: ADMINISTRADOR o DIRECTOR
    
    - **nombre**: Nombre de la unidad (ej: "Regimiento Colorados")
    - **departamento**: Departamento (La Paz, Cochabamba, etc.)
    - **provincia**: Provincia (opcional)
    - **direccion_fisica**: Dirección física de la unidad
    - **capacidad_maxima**: Capacidad máxima de postulantes
    - **jefe_unidad_id**: ID del usuario que será jefe (opcional)
    """
    
    # Validar que el jefe sea válido si se proporciona
    if unidad_data.jefe_unidad_id:
        jefe = db.query(Usuario).filter(Usuario.id == unidad_data.jefe_unidad_id).first()
        if not jefe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {unidad_data.jefe_unidad_id} no encontrado"
            )
        
        if jefe.rol != RolUsuario.JEFE_UNIDAD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario debe tener rol JEFE_UNIDAD, tiene rol {jefe.rol.value}"
            )
    
    # Crear unidad
    nueva_unidad = UnidadReclutamiento(
        nombre=unidad_data.nombre,
        departamento=unidad_data.departamento,
        provincia=unidad_data.provincia,
        direccion_fisica=unidad_data.direccion_fisica,
        capacidad_maxima=unidad_data.capacidad_maxima,
        jefe_unidad_id=unidad_data.jefe_unidad_id
    )
    
    db.add(nueva_unidad)
    db.commit()
    db.refresh(nueva_unidad)
    
    return UnidadCreateResponse(
        id=nueva_unidad.id,
        nombre=nueva_unidad.nombre,
        estado="Creado"
    )

@router.get("/", response_model=List[UnidadResponse])
def listar_unidades(
    db: Session = Depends(get_db)
):
    """
    **Listar todas las unidades de reclutamiento**
    
    No requiere autenticación (Público).
    """
    unidades = db.query(UnidadReclutamiento).all()
    current_year = datetime.now().year
    
    response = []
    for unidad in unidades:
        medicos = []
        supervisores = []
        jefes = []
        
        # Filtrar personal asignado para la gestión actual
        for asignacion in unidad.personal_asignado:
            if asignacion.gestion == current_year:
                # Asegurarse de que el usuario existe (debería por FK, pero por seguridad)
                if not asignacion.usuario:
                    continue
                    
                info = PersonalInfo(
                    id=asignacion.usuario.id,
                    nombres=asignacion.usuario.nombres,
                    paterno=asignacion.usuario.paterno,
                    materno=asignacion.usuario.materno
                )
                
                if asignacion.rol_en_unidad == RolUsuario.MEDICO:
                    medicos.append(info)
                elif asignacion.rol_en_unidad == RolUsuario.SUPERVISOR:
                    supervisores.append(info)
                elif asignacion.rol_en_unidad == RolUsuario.JEFE_UNIDAD:
                    jefes.append(info)
        
        # Crear respuesta de unidad
        unidad_resp = UnidadResponse(
            id=unidad.id,
            nombre=unidad.nombre,
            departamento=unidad.departamento,
            provincia=unidad.provincia,
            direccion_fisica=unidad.direccion_fisica,
            capacidad_maxima=unidad.capacidad_maxima,
            jefe_unidad_id=unidad.jefe_unidad_id,
            medicos=medicos,
            supervisores=supervisores,
            jefes_unidad=jefes
        )
        response.append(unidad_resp)
        
    return response

@router.post("/{unidad_id}/personal", response_model=PersonalAsignadoCreateResponse)
def asignar_personal(
    unidad_id: int,
    personal_data: PersonalAsignadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR", "JEFE_UNIDAD"]))
):
    """
    **Asignar Personal Médico/Supervisor (RF12)**
    
    Asigna médicos o supervisores a una unidad de reclutamiento.
    
    Requiere rol: ADMINISTRADOR, DIRECTOR o JEFE_UNIDAD
    
    - **usuario_id**: ID del médico o supervisor
    - **rol_en_unidad**: "MEDICO" o "SUPERVISOR"
    - **gestion**: Año (ej: 2025)
    """
    
    # Validar que la unidad existe
    unidad = db.query(UnidadReclutamiento).filter(UnidadReclutamiento.id == unidad_id).first()
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unidad con ID {unidad_id} no encontrada"
        )
    
    # Validar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == personal_data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {personal_data.usuario_id} no encontrado"
        )
    
    # Validar que el rol sea MEDICO, SUPERVISOR o JEFE_UNIDAD
    if personal_data.rol_en_unidad not in ["MEDICO", "SUPERVISOR", "JEFE_UNIDAD"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol_en_unidad debe ser 'MEDICO', 'SUPERVISOR' o 'JEFE_UNIDAD'"
        )
    
    # Validar que el usuario tenga el rol correcto
    try:
        rol_enum = RolUsuario(personal_data.rol_en_unidad)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido: {personal_data.rol_en_unidad}"
        )
    
    if usuario.rol != rol_enum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario tiene rol {usuario.rol.value}, se esperaba {personal_data.rol_en_unidad}"
        )
    
    # Verificar si ya está asignado
    asignacion_existente = db.query(PersonalAsignado).filter(
        PersonalAsignado.unidad_id == unidad_id,
        PersonalAsignado.usuario_id == personal_data.usuario_id,
        PersonalAsignado.gestion == personal_data.gestion
    ).first()
    
    if asignacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Este usuario ya está asignado a esta unidad para la gestión {personal_data.gestion}"
        )
    
    # Si es JEFE_UNIDAD, actualizar también el campo en la unidad
    if rol_enum == RolUsuario.JEFE_UNIDAD:
        # Verificar si ya hay un jefe asignado (opcional, o sobrescribir)
        # En este caso sobrescribimos
        unidad.jefe_unidad_id = personal_data.usuario_id
        db.add(unidad)
    
    # Crear asignación
    nueva_asignacion = PersonalAsignado(
        unidad_id=unidad_id,
        usuario_id=personal_data.usuario_id,
        rol_en_unidad=rol_enum,
        gestion=personal_data.gestion
    )
    
    db.add(nueva_asignacion)
    db.commit()
    
    if personal_data.rol_en_unidad == "MEDICO":
        rol_nombre = "Médico"
    elif personal_data.rol_en_unidad == "SUPERVISOR":
        rol_nombre = "Supervisor"
    else:
        rol_nombre = "Jefe de Unidad"
    
    return PersonalAsignadoCreateResponse(
        mensaje=f"{rol_nombre} asignado a la unidad correctamente"
    )

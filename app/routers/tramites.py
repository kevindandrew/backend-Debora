from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import shutil

from app.database import get_db
from app.models.tramite import Tramite, TipoTramite, EstadoTramite
from app.models.requisito_tramite import RequisitoTramite
from app.models.usuario import Usuario
from app.schemas.tramite import (
    TramiteCreate,
    TramiteResponse,
    TramiteDetalle,
    TramiteListItem,
    RequisitoUploadResponse,
    RequisitoDetalle,
    TramiteRespuestaRequest,
    TramiteRespuestaResponse
)
from app.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/api/v1/tramites",
    tags=["Trámites - App Móvil"]
)

# Directorio para guardar requisitos de trámites
REQUISITOS_DIR = Path("uploads/requisitos_tramites")
REQUISITOS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=TramiteResponse)
def solicitar_tramite(
    tramite_data: TramiteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["LICENCIADO", "ADMINISTRADOR"]))
):
    """
    **Solicitar Trámite (RF14, RF16)**
    
    Permite a un licenciado solicitar un trámite desde la app móvil.
    
    Requiere rol: LICENCIADO o ADMINISTRADOR
    
    **Tipos de trámite:**
    - RECTIFICACION: Corrección de datos en documentos
    - PERDIDA: Pérdida de documentos/libreta
    - CERTIFICACION: Solicitud de certificados
    
    **Estados:**
    - SOLICITADO (inicial)
    - EN_REVISION
    - ACEPTADO
    - RECHAZADO
    """
    
    # 1. Validar tipo de trámite
    tipo_valido = tramite_data.tipo_tramite.upper()
    if tipo_valido not in ["RECTIFICACION", "PERDIDA", "CERTIFICACION"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de trámite inválido. Use: RECTIFICACION, PERDIDA o CERTIFICACION"
        )
    
    try:
        tipo_enum = TipoTramite(tipo_valido)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de trámite inválido: {tipo_valido}"
        )
    
    # 2. Crear trámite
    nuevo_tramite = Tramite(
        licenciado_usuario_id=current_user.id,
        tipo=tipo_enum,
        descripcion_solicitud=tramite_data.descripcion,
        estado=EstadoTramite.SOLICITADO
    )
    
    db.add(nuevo_tramite)
    db.commit()
    db.refresh(nuevo_tramite)
    
    return TramiteResponse(
        tramite_id=nuevo_tramite.id,
        estado=EstadoTramite.SOLICITADO.value,
        mensaje="Suba los requisitos."
    )


@router.post("/{tramite_id}/requisitos", response_model=RequisitoUploadResponse)
async def subir_requisito_tramite(
    tramite_id: int,
    nombre_requisito: str = Form(..., description="Nombre del requisito (ej: boleta_deposito, foto_4x4)"),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Subir Requisito de Trámite (RF17)**
    
    Permite subir documentos requeridos para un trámite.
    
    Requiere autenticación.
    
    **Requisitos comunes:**
    - boleta_deposito: Comprobante de pago
    - foto_4x4: Fotografía tamaño carnet
    - ci_copia: Copia de CI
    - declaracion_jurada: Declaración jurada según tipo de trámite
    """
    
    # 1. Verificar que el trámite existe
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trámite con ID {tramite_id} no encontrado"
        )
    
    # 2. Verificar que el usuario sea el dueño del trámite o un admin
    if tramite.licenciado_usuario_id != current_user.id and current_user.rol.value not in ["ADMINISTRADOR", "DIRECTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para subir requisitos a este trámite"
        )
    
    # 3. Validar formato de archivo
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
    file_extension = Path(archivo.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Formatos aceptados: {', '.join(allowed_extensions)}"
        )
    
    # 4. Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"tramite_{tramite_id}_{nombre_requisito}_{timestamp}{file_extension}"
    file_path = REQUISITOS_DIR / safe_filename
    
    # 5. Guardar archivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo: {str(e)}"
        )
    finally:
        archivo.file.close()
    
    # 6. Registrar requisito en la base de datos
    nuevo_requisito = RequisitoTramite(
        tramite_id=tramite_id,
        nombre_requisito=nombre_requisito,
        url_archivo=str(file_path),
        validado=False
    )
    
    db.add(nuevo_requisito)
    db.commit()
    db.refresh(nuevo_requisito)
    
    # 7. Actualizar estado del trámite a EN_REVISION si es el primer requisito
    if tramite.estado == EstadoTramite.SOLICITADO:
        tramite.estado = EstadoTramite.EN_REVISION
        db.commit()
    
    return RequisitoUploadResponse(
        id=nuevo_requisito.id,
        mensaje=f"{nombre_requisito.replace('_', ' ').title()} subida correctamente."
    )


@router.patch("/{tramite_id}/respuesta", response_model=TramiteRespuestaResponse)
def responder_tramite(
    tramite_id: int,
    respuesta_data: TramiteRespuestaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Responder Trámite (Administrador)**
    
    Permite al administrador aprobar o rechazar un trámite del licenciado.
    
    Requiere rol: ADMINISTRADOR o DIRECTOR
    
    **Estados finales:**
    - ACEPTADO: Trámite aprobado
    - RECHAZADO: Trámite rechazado
    """
    
    # 1. Verificar que el trámite existe
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trámite con ID {tramite_id} no encontrado"
        )
    
    # 2. Validar estado de respuesta
    estado_respuesta = respuesta_data.estado.upper()
    if estado_respuesta not in ["ACEPTADO", "RECHAZADO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado debe ser 'ACEPTADO' o 'RECHAZADO'"
        )
    
    try:
        estado_enum = EstadoTramite(estado_respuesta)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido: {estado_respuesta}"
        )
    
    # 3. Actualizar trámite
    tramite.estado = estado_enum
    tramite.respuesta_admin = respuesta_data.respuesta_texto
    
    db.commit()
    db.refresh(tramite)
    
    # 4. Preparar mensaje
    if estado_enum == EstadoTramite.ACEPTADO:
        mensaje = "Respuesta enviada a la App del licenciado. Trámite ACEPTADO."
    else:
        mensaje = "Respuesta enviada a la App del licenciado. Trámite RECHAZADO."
    
    return TramiteRespuestaResponse(
        mensaje=mensaje
    )


@router.get("/", response_model=List[TramiteListItem])
def listar_tramites(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Listar Trámites**
    
    - Si es LICENCIADO: Ve solo sus trámites
    - Si es ADMINISTRADOR/DIRECTOR: Ve todos los trámites
    
    **Filtros:**
    - estado: SOLICITADO, EN_REVISION, ACEPTADO, RECHAZADO
    - tipo: RECTIFICACION, PERDIDA, CERTIFICACION
    """
    
    # Query base
    query = db.query(Tramite)
    
    # Si es licenciado, solo ve sus propios trámites
    if current_user.rol.value == "LICENCIADO":
        query = query.filter(Tramite.licenciado_usuario_id == current_user.id)
    
    # Aplicar filtros
    if estado:
        try:
            estado_enum = EstadoTramite(estado.upper())
            query = query.filter(Tramite.estado == estado_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Estados válidos: {[e.value for e in EstadoTramite]}"
            )
    
    if tipo:
        try:
            tipo_enum = TipoTramite(tipo.upper())
            query = query.filter(Tramite.tipo == tipo_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Tipos válidos: {[t.value for t in TipoTramite]}"
            )
    
    # Ordenar por fecha más reciente
    tramites = query.order_by(Tramite.fecha_solicitud.desc()).all()
    
    return [
        TramiteListItem(
            id=t.id,
            tipo=t.tipo.value,
            descripcion_solicitud=t.descripcion_solicitud,
            estado=t.estado.value,
            fecha_solicitud=t.fecha_solicitud
        )
        for t in tramites
    ]


@router.get("/{tramite_id}", response_model=TramiteDetalle)
def obtener_tramite_detalle(
    tramite_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Obtener detalles de un trámite**
    
    Muestra toda la información del trámite incluyendo respuesta del admin.
    
    Requiere autenticación.
    """
    
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trámite con ID {tramite_id} no encontrado"
        )
    
    # Verificar permisos
    if tramite.licenciado_usuario_id != current_user.id and current_user.rol.value not in ["ADMINISTRADOR", "DIRECTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este trámite"
        )
    
    return TramiteDetalle(
        id=tramite.id,
        licenciado_usuario_id=tramite.licenciado_usuario_id,
        tipo=tramite.tipo.value,
        descripcion_solicitud=tramite.descripcion_solicitud,
        fecha_solicitud=tramite.fecha_solicitud,
        estado=tramite.estado.value,
        respuesta_admin=tramite.respuesta_admin,
        archivo_respuesta_url=tramite.archivo_respuesta_url
    )


@router.get("/{tramite_id}/requisitos", response_model=List[RequisitoDetalle])
def listar_requisitos_tramite(
    tramite_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Listar requisitos de un trámite**
    
    Muestra todos los documentos subidos para un trámite.
    
    Requiere autenticación.
    """
    
    # Verificar que el trámite existe
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trámite con ID {tramite_id} no encontrado"
        )
    
    # Verificar permisos
    if tramite.licenciado_usuario_id != current_user.id and current_user.rol.value not in ["ADMINISTRADOR", "DIRECTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver los requisitos de este trámite"
        )
    
    # Obtener requisitos
    requisitos = db.query(RequisitoTramite).filter(
        RequisitoTramite.tramite_id == tramite_id
    ).all()
    
    return requisitos

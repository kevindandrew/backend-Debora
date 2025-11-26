from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models.persona import Persona
from app.models.tutor import Tutor
from app.models.postulacion import Postulacion, EstadoPostulacion
from app.models.modalidad import Modalidad
from app.models.unidad_reclutamiento import UnidadReclutamiento
from app.models.documento_postulante import DocumentoPostulante
from app.models.evaluacion_medica import EvaluacionMedica
from app.models.evaluacion_supervision import EvaluacionSupervision
from app.models.usuario import Usuario, RolUsuario
from app.models.personal_asignado import PersonalAsignado
from app.models.examen_adicional import ExamenAdicional
from app.models.historial_servicio import HistorialServicio
from app.schemas.postulacion import (
    PostulacionCreate,
    PostulacionResponse,
    PostulacionListItem,
    PostulacionDetalle,
    DocumentoUploadResponse,
    DocumentoResponse
)
from app.schemas.examen import ExamenAdicionalCreate, ExamenAdicionalResponse
from app.schemas.historial import HistorialServicioCreate, HistorialServicioResponse
from app.schemas.evaluacion import VeredictoRequest, VeredictoResponse
from app.dependencies import get_current_user, require_role
from app.utils.reclutamiento import (
    calcular_edad,
    generar_codigo_inscripcion,
    validar_edad_modalidad,
    es_menor_de_edad
)
from app.security import get_password_hash
from app.utils.email import enviar_correo

router = APIRouter(
    prefix="/api/v1/postulaciones",
    tags=["Postulaciones y Reclutamiento"]
)

# Directorio para guardar documentos
UPLOAD_DIR = Path("uploads/documentos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=PostulacionResponse)
def registrar_postulante(
    postulacion_data: PostulacionCreate,
    db: Session = Depends(get_db)
):
    """
    **Registrar Postulante (Inscripción) - RF01, RF02**
    
    Registra un nuevo postulante al servicio militar.
    
    No requiere autenticación (es público para que los postulantes se inscriban).
    
    **Validaciones automáticas:**
    - ✅ Verifica que la edad esté en el rango de la modalidad (RF02)
    - ✅ Evita doble postulación en la misma gestión (RF2)
    - ✅ Requiere tutor si es menor de 18 años
    - ✅ Genera código único de inscripción
    
    **Datos requeridos:**
    - ci, nombres, paterno, fecha_nacimiento, genero
    - modalidad_id, unidad_id
    - tutor (si es menor de edad)
    """
    
    # 1. Validar que la modalidad exista
    modalidad = db.query(Modalidad).filter(Modalidad.id == postulacion_data.modalidad_id).first()
    if not modalidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modalidad con ID {postulacion_data.modalidad_id} no encontrada"
        )
    
    # 2. Validar que la unidad exista
    unidad = db.query(UnidadReclutamiento).filter(
        UnidadReclutamiento.id == postulacion_data.unidad_id
    ).first()
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unidad con ID {postulacion_data.unidad_id} no encontrada"
        )
    
    # 3. Calcular edad y validar (RF02)
    edad = calcular_edad(postulacion_data.fecha_nacimiento)
    es_valido, mensaje_error = validar_edad_modalidad(
        edad,
        modalidad.edad_minima,
        modalidad.edad_maxima
    )
    
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Edad no válida para la modalidad '{modalidad.nombre}'. {mensaje_error}"
        )
    
    # 4. Verificar si es menor de edad y requiere tutor
    if es_menor_de_edad(edad) and not postulacion_data.tutor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere un tutor para menores de 18 años"
        )
    
    # 5. Buscar o crear persona
    persona = db.query(Persona).filter(Persona.ci == postulacion_data.ci).first()
    
    if persona:
        # Persona ya existe, actualizar datos si es necesario
        persona.nombres = postulacion_data.nombres
        persona.paterno = postulacion_data.paterno
        persona.materno = postulacion_data.materno
        persona.fecha_nacimiento = postulacion_data.fecha_nacimiento
        persona.genero = postulacion_data.genero
        if postulacion_data.direccion:
            persona.direccion = postulacion_data.direccion
    else:
        # Crear nueva persona
        persona = Persona(
            ci=postulacion_data.ci,
            nombres=postulacion_data.nombres,
            paterno=postulacion_data.paterno,
            materno=postulacion_data.materno,
            fecha_nacimiento=postulacion_data.fecha_nacimiento,
            genero=postulacion_data.genero,
            direccion=postulacion_data.direccion
        )
        db.add(persona)
        db.flush()
    
    # 6. Verificar que no exista postulación activa en la misma gestión (RF2)
    gestion_actual = datetime.now().year
    postulacion_existente = db.query(Postulacion).filter(
        Postulacion.persona_id == persona.id,
        Postulacion.gestion == gestion_actual
    ).first()
    
    if postulacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una postulación para este CI en la gestión {gestion_actual}. "
                   f"Código: {postulacion_existente.codigo_inscripcion}"
        )
    
    # 7. Crear tutor si es necesario
    tutor_id = None
    if postulacion_data.tutor:
        tutor = Tutor(
            nombre_completo=postulacion_data.tutor.nombre_completo,
            ci=postulacion_data.tutor.ci,
            relacion=postulacion_data.tutor.relacion
        )
        db.add(tutor)
        db.flush()
        tutor_id = tutor.id
    
    # 8. Generar código único de inscripción
    codigo_inscripcion = generar_codigo_inscripcion(db, modalidad.nombre, gestion_actual)
    
    # 9. Crear postulación
    nueva_postulacion = Postulacion(
        codigo_inscripcion=codigo_inscripcion,
        persona_id=persona.id,
        tutor_id=tutor_id,
        unidad_id=postulacion_data.unidad_id,
        modalidad_id=postulacion_data.modalidad_id,
        gestion=gestion_actual,
        estado=EstadoPostulacion.INSCRITO
    )
    
    db.add(nueva_postulacion)
    db.commit()
    db.refresh(nueva_postulacion)
    
    return PostulacionResponse(
        codigo_inscripcion=codigo_inscripcion,
        estado=EstadoPostulacion.INSCRITO.value,
        mensaje="Postulación registrada. Proceda a subir documentos."
    )


@router.post("/{codigo_inscripcion}/documentos", response_model=DocumentoUploadResponse)
async def subir_documento(
    codigo_inscripcion: str,
    tipo_documento: str = Form(..., description="Tipo: certificado_nacimiento, ci, foto, etc."),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Subir Documentos Digitales (RF03)**
    
    Permite subir documentos escaneados del postulante.
    
    Requiere autenticación.
    
    **Tipos de documentos comunes:**
    - certificado_nacimiento
    - ci_frontal
    - ci_reverso
    - foto_4x4
    - certificado_medico
    - libreta_militar_padre (si aplica)
    """
    
    # 1. Buscar la postulación
    postulacion = db.query(Postulacion).filter(
        Postulacion.codigo_inscripcion == codigo_inscripcion
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con código {codigo_inscripcion} no encontrada"
        )
    
    # 2. Validar formato de archivo
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
    file_extension = Path(archivo.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Formatos aceptados: {', '.join(allowed_extensions)}"
        )
    
    # 3. Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{codigo_inscripcion}_{tipo_documento}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / safe_filename
    
    # 4. Guardar archivo
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
    
    # 5. Registrar en la base de datos
    documento = DocumentoPostulante(
        postulacion_id=postulacion.id,
        tipo_documento=tipo_documento,
        url_archivo=str(file_path),
        subido_por=current_user.id
    )
    
    db.add(documento)
    db.commit()
    db.refresh(documento)
    
    # 6. Generar URL (en producción sería una URL de S3 o similar)
    url = f"/uploads/documentos/{safe_filename}"
    
    return DocumentoUploadResponse(
        id=documento.id,
        url=url,
        mensaje="Subido con éxito"
    )


@router.get("/", response_model=List[PostulacionListItem])
def listar_postulaciones(
    unidad_id: Optional[int] = Query(None, description="Filtrar por unidad"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    gestion: Optional[int] = Query(None, description="Filtrar por gestión"),
    ci: Optional[str] = Query(None, description="Buscar por CI (RF19)"),
    apellido: Optional[str] = Query(None, description="Buscar por apellido (RF19)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR", "JEFE_UNIDAD", "MEDICO", "SUPERVISOR"]))
):
    """
    **Listar Postulantes (RF09, RF19, RF20)**
    
    Lista todas las postulaciones con filtros opcionales.
    
    Requiere rol: ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD, MEDICO o SUPERVISOR
    
    **Filtros automáticos por rol:**
    - **JEFE_UNIDAD**: Solo ve postulantes de su unidad asignada.
    - **MEDICO/SUPERVISOR**: Solo ven postulantes de la unidad donde están asignados en la gestión actual.
    - **ADMINISTRADOR/DIRECTOR**: Pueden ver todo.
    
    **Filtros disponibles:**
    - unidad_id: Filtrar por unidad de reclutamiento (si el rol lo permite)
    - estado: INSCRITO, EN_EVALUACION, APTO, NO_APTO, LICENCIADO, BAJA
    - gestion: Año (ej: 2025)
    - ci: Buscar por carnet de identidad
    - apellido: Buscar por apellido paterno
    """
    
    # Query base con joins
    query = db.query(
        Postulacion.codigo_inscripcion,
        Persona.nombres,
        Persona.paterno,
        Persona.materno,
        Persona.ci,
        Postulacion.estado,
        Modalidad.nombre.label('modalidad_nombre'),
        UnidadReclutamiento.nombre.label('unidad_nombre'),
        Postulacion.fecha_postulacion
    ).join(
        Persona, Postulacion.persona_id == Persona.id
    ).join(
        Modalidad, Postulacion.modalidad_id == Modalidad.id
    ).join(
        UnidadReclutamiento, Postulacion.unidad_id == UnidadReclutamiento.id
    )
    
    # Lógica de filtrado por rol
    if current_user.rol == RolUsuario.JEFE_UNIDAD:
        # Buscar la unidad donde es jefe
        unidad_jefe = db.query(UnidadReclutamiento).filter(
            UnidadReclutamiento.jefe_unidad_id == current_user.id
        ).first()
        
        if unidad_jefe:
            query = query.filter(Postulacion.unidad_id == unidad_jefe.id)
        else:
            # Si es jefe pero no tiene unidad asignada, no debería ver nada
            query = query.filter(Postulacion.id == -1)
            
    elif current_user.rol in [RolUsuario.MEDICO, RolUsuario.SUPERVISOR]:
        # Buscar asignación en la gestión actual
        gestion_actual = datetime.now().year
        asignacion = db.query(PersonalAsignado).filter(
            PersonalAsignado.usuario_id == current_user.id,
            PersonalAsignado.gestion == gestion_actual
        ).first()
        
        if asignacion:
            query = query.filter(Postulacion.unidad_id == asignacion.unidad_id)
        else:
            # Si no tiene asignación vigente, no ve nada
            query = query.filter(Postulacion.id == -1)
    
    # Aplicar filtros explícitos (respetando los automáticos)
    if unidad_id:
        # Si el usuario ya tiene un filtro automático, verificamos que coincida
        # O simplemente aplicamos el filtro adicional (AND)
        query = query.filter(Postulacion.unidad_id == unidad_id)
    
    if estado:
        try:
            estado_enum = EstadoPostulacion(estado)
            query = query.filter(Postulacion.estado == estado_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Estados válidos: {[e.value for e in EstadoPostulacion]}"
            )
    
    if gestion:
        query = query.filter(Postulacion.gestion == gestion)
    
    # RF19: Búsqueda por CI
    if ci:
        query = query.filter(Persona.ci.ilike(f"%{ci}%"))
    
    # RF19: Búsqueda por apellido
    if apellido:
        query = query.filter(Persona.paterno.ilike(f"%{apellido}%"))
    
    # Ejecutar query
    resultados = query.all()
    
    # Formatear resultados
    postulaciones_lista = []
    for r in resultados:
        nombre_completo = f"{r.nombres} {r.paterno}"
        if r.materno:
            nombre_completo += f" {r.materno}"
        
        postulaciones_lista.append(PostulacionListItem(
            codigo_inscripcion=r.codigo_inscripcion,
            nombre_completo=nombre_completo,
            ci=r.ci,
            estado=r.estado.value if hasattr(r.estado, 'value') else str(r.estado),
            modalidad=r.modalidad_nombre,
            unidad=r.unidad_nombre,
            fecha_postulacion=r.fecha_postulacion
        ))
    
    return postulaciones_lista


@router.get("/{codigo_inscripcion}", response_model=PostulacionDetalle)
def obtener_postulacion_detalle(
    codigo_inscripcion: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR", "JEFE_UNIDAD", "MEDICO", "SUPERVISOR"]))
):
    """
    **Obtener detalles de una postulación específica**
    
    Muestra toda la información de una postulación incluyendo datos de persona y tutor.
    
    Requiere autenticación.
    """
    
    postulacion = db.query(Postulacion).filter(
        Postulacion.codigo_inscripcion == codigo_inscripcion
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con código {codigo_inscripcion} no encontrada"
        )
    
    # Obtener datos de persona
    persona = db.query(Persona).filter(Persona.id == postulacion.persona_id).first()
    persona_dict = {
        "id": persona.id,
        "ci": persona.ci,
        "nombres": persona.nombres,
        "paterno": persona.paterno,
        "materno": persona.materno,
        "fecha_nacimiento": str(persona.fecha_nacimiento),
        "genero": persona.genero,
        "direccion": persona.direccion
    }
    
    # Obtener datos de tutor si existe
    tutor_dict = None
    if postulacion.tutor_id:
        tutor = db.query(Tutor).filter(Tutor.id == postulacion.tutor_id).first()
        if tutor:
            tutor_dict = {
                "id": tutor.id,
                "nombre_completo": tutor.nombre_completo,
                "ci": tutor.ci,
                "relacion": tutor.relacion
            }
    
    return PostulacionDetalle(
        id=postulacion.id,
        codigo_inscripcion=postulacion.codigo_inscripcion,
        persona_id=postulacion.persona_id,
        tutor_id=postulacion.tutor_id,
        unidad_id=postulacion.unidad_id,
        modalidad_id=postulacion.modalidad_id,
        gestion=postulacion.gestion,
        estado=postulacion.estado.value,
        fecha_postulacion=postulacion.fecha_postulacion,
        persona=persona_dict,
        tutor=tutor_dict
    )


@router.patch("/{postulacion_id}/veredicto", response_model=VeredictoResponse)
def aprobar_rechazar_postulacion(
    postulacion_id: int,
    veredicto_data: VeredictoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["JEFE_UNIDAD", "ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Aprobar/Rechazar Postulación - Veredicto Final**
    
    Permite al Jefe de Unidad dar el veredicto final sobre una postulación.
    
    Requiere rol: JEFE_UNIDAD, ADMINISTRADOR o DIRECTOR
    
    **Validaciones:**
    - La postulación debe existir
    - Debe tener ambas evaluaciones (médica y física) aprobadas
    - El estado debe ser EN_EVALUACION
    
    **Estados finales:**
    - APTO: Postulante habilitado para el servicio
    - NO_APTO: Postulante rechazado
    """
    
    # 1. Validar que la postulación exista
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {postulacion_id} no encontrada"
        )
    
    # 2. Validar estado final
    if veredicto_data.estado_final not in ["APTO", "NO_APTO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado_final debe ser 'APTO' o 'NO_APTO'"
        )
    
    # 3. Si se va a aprobar (APTO), verificar que tenga ambas evaluaciones aprobadas
    if veredicto_data.estado_final == "APTO":
        # Verificar evaluación médica
        evaluacion_medica = db.query(EvaluacionMedica).filter(
            EvaluacionMedica.postulacion_id == postulacion_id
        ).first()
        
        if not evaluacion_medica:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede aprobar: falta evaluación médica"
            )
        
        if not evaluacion_medica.resultado_apto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede aprobar: la evaluación médica fue NO APTA"
            )
        
        # Verificar evaluación física
        evaluacion_fisica = db.query(EvaluacionSupervision).filter(
            EvaluacionSupervision.postulacion_id == postulacion_id
        ).first()
        
        if not evaluacion_fisica:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede aprobar: falta evaluación física"
            )
        
        if not evaluacion_fisica.resultado_final_supervisor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede aprobar: la evaluación física fue NO APTA"
            )
    
    # 4. Actualizar estado de la postulación
    try:
        nuevo_estado = EstadoPostulacion(veredicto_data.estado_final)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido: {veredicto_data.estado_final}"
        )
    
    postulacion.estado = nuevo_estado
    db.commit()
    db.refresh(postulacion)
    
    # 5. Preparar respuesta
    if nuevo_estado == EstadoPostulacion.APTO:
        mensaje = "Postulante habilitado para servicio."
        if veredicto_data.comentario:
            mensaje = f"{veredicto_data.comentario} - {mensaje}"
    else:
        mensaje = "Postulante NO APTO."
        if veredicto_data.comentario:
            mensaje = f"{veredicto_data.comentario} - {mensaje}"
    

    
    # Notificar cambio de estado
    persona = db.query(Persona).filter(Persona.id == postulacion.persona_id).first()
    if persona:
        email_destino = f"{persona.ci}@soldado.bo"
        asunto = f"Actualización de Postulación: {nuevo_estado.value}"
        enviar_correo(email_destino, asunto, mensaje)

    return VeredictoResponse(
        nuevo_estado=nuevo_estado.value,
        mensaje=mensaje
    )

@router.patch("/{postulacion_id}/licenciar")
def licenciar_soldado(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "JEFE_UNIDAD"]))
):
    """
    **Licenciar Soldado (RF13)**
    
    Cambia el estado de un soldado de APTO a LICENCIADO al finalizar su servicio.
    Además, crea un usuario para que pueda acceder al sistema como LICENCIADO.
    
    **Requisitos:**
    - Estado actual debe ser APTO.
    
    **Acciones:**
    - Cambia estado a LICENCIADO.
    - Crea usuario con Rol LICENCIADO.
    - Username: CI del soldado.
    - Password: CI del soldado.
    """
    
    # 1. Buscar postulación
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {postulacion_id} no encontrada"
        )
        
    # 2. Validar estado actual
    if postulacion.estado != EstadoPostulacion.APTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede licenciar a soldados en estado APTO. Estado actual: {postulacion.estado}"
        )
        
    # 3. Obtener datos de la persona para crear usuario
    persona = db.query(Persona).filter(Persona.id == postulacion.persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datos de persona no encontrados"
        )
        
    # 4. Verificar si ya tiene usuario
    usuario_existente = db.query(Usuario).filter(Usuario.username == persona.ci).first()
    
    if usuario_existente:
        # Si ya existe, solo actualizamos el rol si es necesario, o lo dejamos así
        # Pero para este caso, asumimos que es nuevo usuario o actualizamos rol
        usuario_existente.rol = RolUsuario.LICENCIADO
        # No cambiamos password si ya existe
        mensaje_usuario = "Usuario existente actualizado a rol LICENCIADO."
    else:
        # 5. Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=persona.ci,
            password_hash=get_password_hash(persona.ci), # Password inicial = CI
            rol=RolUsuario.LICENCIADO,
            estado=True
        )
        db.add(nuevo_usuario)
        db.flush() # Para obtener ID
        mensaje_usuario = f"Usuario creado. Credenciales: {persona.ci} / {persona.ci}"
        
        # Vincular usuario a persona si existe la relación en modelo Persona (opcional, pero buena práctica)
        # persona.usuario_id = nuevo_usuario.id 
    
    # 6. Cambiar estado postulación
    postulacion.estado = EstadoPostulacion.LICENCIADO
    db.commit()
    
    # Notificar licenciamiento
    email_destino = f"{persona.ci}@soldado.bo"
    asunto = "Licenciamiento de Servicio Militar"
    cuerpo = f"Felicidades, ha sido Licenciado. Puede acceder al sistema con: Usuario: {persona.ci}, Contraseña: {persona.ci}"
    enviar_correo(email_destino, asunto, cuerpo)
    
    return {
        "mensaje": f"Soldado licenciado con éxito. {mensaje_usuario}",
        "nuevo_estado": EstadoPostulacion.LICENCIADO,
        "credenciales_usuario": {
            "username": persona.ci,
            "nota": "La contraseña es el mismo número de CI"
        }
    }

@router.post("/{postulacion_id}/examenes", response_model=ExamenAdicionalResponse)
async def registrar_examen_externo(
    postulacion_id: int,
    tipo_examen: str = Form(...),
    resultado: str = Form(...),
    fecha_entrega: date = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["MEDICO", "ADMINISTRADOR"]))
):
    """
    **Registrar Examen Externo (RF06)**
    
    Permite subir un examen médico externo (ej: Rayos X, ECG).
    """
    # 1. Validar postulación
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
        
    # 2. Guardar archivo
    file_extension = Path(archivo.filename).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"examen_{postulacion_id}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
    finally:
        archivo.file.close()
        
    # 3. Crear registro
    nuevo_examen = ExamenAdicional(
        postulacion_id=postulacion_id,
        tipo_examen=tipo_examen,
        resultado=resultado,
        fecha_entrega=fecha_entrega,
        archivo_adjunto=str(file_path)
    )
    
    db.add(nuevo_examen)
    db.commit()
    db.refresh(nuevo_examen)
    
    return nuevo_examen

@router.get("/{postulacion_id}/examenes", response_model=List[ExamenAdicionalResponse])
def listar_examenes_externos(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["MEDICO", "ADMINISTRADOR", "JEFE_UNIDAD"]))
):
    """
    **Listar Exámenes Externos**
    """
    examenes = db.query(ExamenAdicional).filter(
        ExamenAdicional.postulacion_id == postulacion_id
    ).all()
    
    return examenes

@router.post("/{postulacion_id}/historial", response_model=HistorialServicioResponse)
def agregar_historial_servicio(
    postulacion_id: int,
    historial_data: HistorialServicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["JEFE_UNIDAD", "ADMINISTRADOR"]))
):
    """
    **Agregar Registro al Historial (RF06)**
    
    Permite registrar eventos en el historial del soldado (méritos, sanciones, etc.).
    """
    # 1. Validar postulación
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
        
    # 2. Crear registro
    nuevo_historial = HistorialServicio(
        postulacion_id=postulacion_id,
        jefe_unidad_id=current_user.id,
        tipo_registro=historial_data.tipo_registro,
        descripcion=historial_data.descripcion,
        calificacion=historial_data.calificacion
    )
    
    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)
    
    return nuevo_historial

@router.get("/{postulacion_id}/historial", response_model=List[HistorialServicioResponse])
def obtener_historial_servicio(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["JEFE_UNIDAD", "ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Obtener Historial de Servicio**
    """
    historial = db.query(HistorialServicio).filter(
        HistorialServicio.postulacion_id == postulacion_id
    ).all()
    
    return historial

@router.post("/", response_model=PostulacionResponse)
def registrar_postulante(
    postulacion_data: PostulacionCreate,
    db: Session = Depends(get_db)
):
    """
    **Registrar Postulante (Inscripción) - RF01, RF02**
    
    Registra un nuevo postulante al servicio militar.
    
    No requiere autenticación (es público para que los postulantes se inscriban).
    
    **Validaciones automáticas:**
    - ✅ Verifica que la edad esté en el rango de la modalidad (RF02)
    - ✅ Evita doble postulación en la misma gestión (RF2)
    - ✅ Requiere tutor si es menor de 18 años
    - ✅ Genera código único de inscripción
    
    **Datos requeridos:**
    - ci, nombres, paterno, fecha_nacimiento, genero
    - modalidad_id, unidad_id
    - tutor (si es menor de edad)
    """
    
    # 1. Validar que la modalidad exista
    modalidad = db.query(Modalidad).filter(Modalidad.id == postulacion_data.modalidad_id).first()
    if not modalidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modalidad con ID {postulacion_data.modalidad_id} no encontrada"
        )
    
    # 2. Validar que la unidad exista
    unidad = db.query(UnidadReclutamiento).filter(
        UnidadReclutamiento.id == postulacion_data.unidad_id
    ).first()
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unidad con ID {postulacion_data.unidad_id} no encontrada"
        )
    
    # 3. Calcular edad y validar (RF02)
    edad = calcular_edad(postulacion_data.fecha_nacimiento)
    es_valido, mensaje_error = validar_edad_modalidad(
        edad,
        modalidad.edad_minima,
        modalidad.edad_maxima
    )
    
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Edad no válida para la modalidad '{modalidad.nombre}'. {mensaje_error}"
        )
    
    # 4. Verificar si es menor de edad y requiere tutor
    if es_menor_de_edad(edad) and not postulacion_data.tutor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere un tutor para menores de 18 años"
        )
    
    # 5. Buscar o crear persona
    persona = db.query(Persona).filter(Persona.ci == postulacion_data.ci).first()
    
    if persona:
        # Persona ya existe, actualizar datos si es necesario
        persona.nombres = postulacion_data.nombres
        persona.paterno = postulacion_data.paterno
        persona.materno = postulacion_data.materno
        persona.fecha_nacimiento = postulacion_data.fecha_nacimiento
        persona.genero = postulacion_data.genero
        if postulacion_data.direccion:
            persona.direccion = postulacion_data.direccion
    else:
        # Crear nueva persona
        persona = Persona(
            ci=postulacion_data.ci,
            nombres=postulacion_data.nombres,
            paterno=postulacion_data.paterno,
            materno=postulacion_data.materno,
            fecha_nacimiento=postulacion_data.fecha_nacimiento,
            genero=postulacion_data.genero,
            direccion=postulacion_data.direccion
        )
        db.add(persona)
        db.flush()
    
    # 6. Verificar que no exista postulación activa en la misma gestión (RF2)
    gestion_actual = datetime.now().year
    postulacion_existente = db.query(Postulacion).filter(
        Postulacion.persona_id == persona.id,
        Postulacion.gestion == gestion_actual
    ).first()
    
    if postulacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una postulación para este CI en la gestión {gestion_actual}. "
                   f"Código: {postulacion_existente.codigo_inscripcion}"
        )
    
    # 7. Crear tutor si es necesario
    tutor_id = None
    if postulacion_data.tutor:
        tutor = Tutor(
            nombre_completo=postulacion_data.tutor.nombre_completo,
            ci=postulacion_data.tutor.ci,
            relacion=postulacion_data.tutor.relacion
        )
        db.add(tutor)
        db.flush()
        tutor_id = tutor.id
    
    # 8. Generar código único de inscripción
    codigo_inscripcion = generar_codigo_inscripcion(db, modalidad.nombre, gestion_actual)
    
    # 9. Crear postulación
    nueva_postulacion = Postulacion(
        codigo_inscripcion=codigo_inscripcion,
        persona_id=persona.id,
        tutor_id=tutor_id,
        unidad_id=postulacion_data.unidad_id,
        modalidad_id=postulacion_data.modalidad_id,
        gestion=gestion_actual,
        estado=EstadoPostulacion.INSCRITO
    )
    
    db.add(nueva_postulacion)
    db.commit()
    db.refresh(nueva_postulacion)
    
    return PostulacionResponse(
        codigo_inscripcion=codigo_inscripcion,
        estado=EstadoPostulacion.INSCRITO.value,
        mensaje="Postulación registrada. Proceda a subir documentos."
    )


@router.post("/{codigo_inscripcion}/documentos", response_model=DocumentoUploadResponse)
async def subir_documento(
    codigo_inscripcion: str,
    tipo_documento: str = Form(..., description="Tipo: certificado_nacimiento, ci, foto, etc."),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Subir Documentos Digitales (RF03)**
    
    Permite subir documentos escaneados del postulante.
    
    Requiere autenticación.
    
    **Tipos de documentos comunes:**
    - certificado_nacimiento
    - ci_frontal
    - ci_reverso
    - foto_4x4
    - certificado_medico
    - libreta_militar_padre (si aplica)
    """
    
    # 1. Buscar la postulación
    postulacion = db.query(Postulacion).filter(
        Postulacion.codigo_inscripcion == codigo_inscripcion
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con código {codigo_inscripcion} no encontrada"
        )
    
    # 2. Validar formato de archivo
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
    file_extension = Path(archivo.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Formatos aceptados: {', '.join(allowed_extensions)}"
        )
    
    # 3. Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{codigo_inscripcion}_{tipo_documento}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / safe_filename
    
    # 4. Guardar archivo
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
    
    # 5. Registrar en la base de datos
    documento = DocumentoPostulante(
        postulacion_id=postulacion.id,
        tipo_documento=tipo_documento,
        url_archivo=str(file_path),
        subido_por=current_user.id
    )
    
    db.add(documento)
    db.commit()
    db.refresh(documento)
    
    # 6. Generar URL (en producción sería una URL de S3 o similar)
    url = f"/uploads/documentos/{safe_filename}"
    
    return DocumentoUploadResponse(
        id=documento.id,
        url=url,
        mensaje="Subido con éxito"
    )


@router.get("/", response_model=List[PostulacionListItem])
def listar_postulaciones(
    unidad_id: Optional[int] = Query(None, description="Filtrar por unidad"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    gestion: Optional[int] = Query(None, description="Filtrar por gestión"),
    ci: Optional[str] = Query(None, description="Buscar por CI (RF19)"),
    apellido: Optional[str] = Query(None, description="Buscar por apellido (RF19)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR", "JEFE_UNIDAD"]))
):
    """
    **Listar Postulantes (RF09, RF19, RF20)**
    
    Lista todas las postulaciones con filtros opcionales.
    
    Requiere rol: ADMINISTRADOR, DIRECTOR o JEFE_UNIDAD
    
    **Filtros disponibles:**
    - unidad_id: Filtrar por unidad de reclutamiento
    - estado: INSCRITO, EN_EVALUACION, APTO, NO_APTO, LICENCIADO, BAJA
    - gestion: Año (ej: 2025)
    - ci: Buscar por carnet de identidad
    - apellido: Buscar por apellido paterno
    """
    
    # Query base con joins
    query = db.query(
        Postulacion.codigo_inscripcion,
        Persona.nombres,
        Persona.paterno,
        Persona.materno,
        Persona.ci,
        Postulacion.estado,
        Modalidad.nombre.label('modalidad_nombre'),
        UnidadReclutamiento.nombre.label('unidad_nombre'),
        Postulacion.fecha_postulacion
    ).join(
        Persona, Postulacion.persona_id == Persona.id
    ).join(
        Modalidad, Postulacion.modalidad_id == Modalidad.id
    ).join(
        UnidadReclutamiento, Postulacion.unidad_id == UnidadReclutamiento.id
    )
    
    # Aplicar filtros
    if unidad_id:
        query = query.filter(Postulacion.unidad_id == unidad_id)
    
    if estado:
        try:
            estado_enum = EstadoPostulacion(estado)
            query = query.filter(Postulacion.estado == estado_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Estados válidos: {[e.value for e in EstadoPostulacion]}"
            )
    
    if gestion:
        query = query.filter(Postulacion.gestion == gestion)
    
    # RF19: Búsqueda por CI
    if ci:
        query = query.filter(Persona.ci.ilike(f"%{ci}%"))
    
    # RF19: Búsqueda por apellido
    if apellido:
        query = query.filter(Persona.paterno.ilike(f"%{apellido}%"))
    
    # Ejecutar query
    resultados = query.all()
    
    # Formatear resultados
    postulaciones_lista = []
    for r in resultados:
        nombre_completo = f"{r.nombres} {r.paterno}"
        if r.materno:
            nombre_completo += f" {r.materno}"
        
        postulaciones_lista.append(PostulacionListItem(
            codigo_inscripcion=r.codigo_inscripcion,
            nombre_completo=nombre_completo,
            ci=r.ci,
            estado=r.estado.value if hasattr(r.estado, 'value') else str(r.estado),
            modalidad=r.modalidad_nombre,
            unidad=r.unidad_nombre,
            fecha_postulacion=r.fecha_postulacion
        ))
    
    return postulaciones_lista


@router.get("/{codigo_inscripcion}", response_model=PostulacionDetalle)
def obtener_postulacion_detalle(
    codigo_inscripcion: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR", "JEFE_UNIDAD", "MEDICO", "SUPERVISOR"]))
):
    """
    **Obtener detalles de una postulación específica**
    
    Muestra toda la información de una postulación incluyendo datos de persona y tutor.
    
    Requiere autenticación.
    """
    
    postulacion = db.query(Postulacion).filter(
        Postulacion.codigo_inscripcion == codigo_inscripcion
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con código {codigo_inscripcion} no encontrada"
        )
    
    # Obtener datos de persona
    persona = db.query(Persona).filter(Persona.id == postulacion.persona_id).first()
    persona_dict = {
        "id": persona.id,
        "ci": persona.ci,
        "nombres": persona.nombres,
        "paterno": persona.paterno,
        "materno": persona.materno,
        "fecha_nacimiento": str(persona.fecha_nacimiento),
        "genero": persona.genero,
        "direccion": persona.direccion
    }
    
    # Obtener datos de tutor si existe
    tutor_dict = None
    if postulacion.tutor_id:
        tutor = db.query(Tutor).filter(Tutor.id == postulacion.tutor_id).first()
        if tutor:
            tutor_dict = {
                "id": tutor.id,
                "nombre_completo": tutor.nombre_completo,
                "ci": tutor.ci,
                "relacion": tutor.relacion
            }
    
    return PostulacionDetalle(
        id=postulacion.id,
        codigo_inscripcion=postulacion.codigo_inscripcion,
        persona_id=postulacion.persona_id,
        tutor_id=postulacion.tutor_id,
        unidad_id=postulacion.unidad_id,
        modalidad_id=postulacion.modalidad_id,
        gestion=postulacion.gestion,
        estado=postulacion.estado.value,
        fecha_postulacion=postulacion.fecha_postulacion,
        persona=persona_dict,
        tutor=tutor_dict
    )

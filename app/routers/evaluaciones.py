from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, time as time_type
from typing import Optional

from app.database import get_db
from app.models.postulacion import Postulacion, EstadoPostulacion
from app.models.evaluacion_medica import EvaluacionMedica
from app.models.evaluacion_supervision import EvaluacionSupervision
from app.models.usuario import Usuario
from app.schemas.evaluacion import (
    EvaluacionMedicaCreate,
    EvaluacionMedicaResponse,
    EvaluacionMedicaDetalle,
    EvaluacionFisicaCreate,
    EvaluacionFisicaResponse,
    EvaluacionFisicaDetalle,
    VeredictoRequest,
    VeredictoResponse
)
from app.dependencies import require_role, get_current_user

router = APIRouter(
    prefix="/api/v1/evaluaciones",
    tags=["Evaluaciones Médicas y Físicas"]
)

def convertir_tiempo_str_a_time(tiempo_str: str) -> time_type:
    """
    Convierte string de tiempo (MM:SS o HH:MM:SS) a objeto time
    Ejemplos: "14:30" -> 00:14:30, "1:14:30" -> 01:14:30
    """
    partes = tiempo_str.split(":")
    
    if len(partes) == 2:  # MM:SS
        minutos, segundos = partes
        return time_type(hour=0, minute=int(minutos), second=int(segundos))
    elif len(partes) == 3:  # HH:MM:SS
        horas, minutos, segundos = partes
        return time_type(hour=int(horas), minute=int(minutos), second=int(segundos))
    else:
        raise ValueError("Formato de tiempo inválido. Use MM:SS o HH:MM:SS")

@router.post("/medica", response_model=EvaluacionMedicaResponse)
def registrar_evaluacion_medica(
    evaluacion_data: EvaluacionMedicaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["MEDICO", "ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Registrar Evaluación Médica (RF04)**
    
    Permite a un médico registrar la evaluación médica de un postulante.
    
    Requiere rol: MEDICO o ADMINISTRADOR
    
    **Validaciones:**
    - La postulación debe existir
    - No debe tener evaluación médica previa
    - Cambia el estado de la postulación a EN_EVALUACION
    
    **Campos:**
    - peso, estatura, grupo_sanguineo
    - Características físicas (color piel, ojos, nariz, boca)
    - prueba_embarazo (solo mujeres)
    - resultado_apto: true/false
    """
    
    # 1. Validar que la postulación exista
    postulacion = db.query(Postulacion).filter(
        Postulacion.id == evaluacion_data.postulacion_id
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {evaluacion_data.postulacion_id} no encontrada"
        )
    
    # 2. Verificar que no tenga evaluación médica previa
    evaluacion_existente = db.query(EvaluacionMedica).filter(
        EvaluacionMedica.postulacion_id == evaluacion_data.postulacion_id
    ).first()
    
    if evaluacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta postulación ya tiene una evaluación médica registrada"
        )
    
    # 3. Crear evaluación médica
    nueva_evaluacion = EvaluacionMedica(
        postulacion_id=evaluacion_data.postulacion_id,
        medico_id=current_user.id,
        peso=evaluacion_data.peso,
        estatura=evaluacion_data.estatura,
        grupo_sanguineo=evaluacion_data.grupo_sanguineo,
        color_piel=evaluacion_data.color_piel,
        color_ojos=evaluacion_data.color_ojos,
        tipo_nariz=evaluacion_data.tipo_nariz,
        tipo_boca=evaluacion_data.tipo_boca,
        prueba_embarazo=evaluacion_data.prueba_embarazo,
        observaciones=evaluacion_data.observaciones,
        resultado_apto=evaluacion_data.resultado_apto
    )
    
    db.add(nueva_evaluacion)
    
    # 4. Actualizar estado de la postulación
    if postulacion.estado == EstadoPostulacion.INSCRITO:
        postulacion.estado = EstadoPostulacion.EN_EVALUACION
    
    # Si la evaluación médica es NO APTO, marcar como NO_APTO directamente
    if not evaluacion_data.resultado_apto:
        postulacion.estado = EstadoPostulacion.NO_APTO
    
    db.commit()
    db.refresh(nueva_evaluacion)
    
    # 5. Determinar siguiente paso
    if evaluacion_data.resultado_apto:
        siguiente_paso = "Evaluación Física"
        estado_mensaje = "Evaluado - Apto Médicamente"
    else:
        siguiente_paso = "Postulación Rechazada - No Apto Médicamente"
        estado_mensaje = "No Apto"
    
    return EvaluacionMedicaResponse(
        id=nueva_evaluacion.id,
        estado=estado_mensaje,
        siguiente_paso=siguiente_paso
    )


@router.get("/medica/{postulacion_id}", response_model=EvaluacionMedicaDetalle)
def obtener_evaluacion_medica(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Obtener Evaluación Médica de una postulación**
    
    Muestra los detalles de la evaluación médica.
    
    Requiere autenticación.
    """
    
    evaluacion = db.query(EvaluacionMedica).filter(
        EvaluacionMedica.postulacion_id == postulacion_id
    ).first()
    
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró evaluación médica para esta postulación"
        )
    
    return evaluacion


@router.post("/fisica", response_model=EvaluacionFisicaResponse)
def registrar_evaluacion_fisica(
    evaluacion_data: EvaluacionFisicaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPERVISOR", "ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Registrar Evaluación Física/Supervisión (RF05)**
    
    Permite a un supervisor registrar la evaluación física del postulante.
    
    Requiere rol: SUPERVISOR o ADMINISTRADOR
    
    **Validaciones:**
    - La postulación debe existir
    - Debe tener evaluación médica aprobada
    - No debe tener evaluación física previa
    
    **Campos:**
    - flexiones, abdominales, carrera_3200m
    - Habilidades: sabe_leer, sabe_escribir, sabe_conducir
    - resultado_psicologico
    - resultado_final_supervisor: true/false
    """
    
    # 1. Validar que la postulación exista
    postulacion = db.query(Postulacion).filter(
        Postulacion.id == evaluacion_data.postulacion_id
    ).first()
    
    if not postulacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {evaluacion_data.postulacion_id} no encontrada"
        )
    
    # 2. Verificar que tenga evaluación médica aprobada
    evaluacion_medica = db.query(EvaluacionMedica).filter(
        EvaluacionMedica.postulacion_id == evaluacion_data.postulacion_id
    ).first()
    
    if not evaluacion_medica:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El postulante debe pasar primero la evaluación médica"
        )
    
    if not evaluacion_medica.resultado_apto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El postulante no es apto médicamente, no puede continuar con evaluación física"
        )
    
    # 3. Verificar que no tenga evaluación física previa
    evaluacion_existente = db.query(EvaluacionSupervision).filter(
        EvaluacionSupervision.postulacion_id == evaluacion_data.postulacion_id
    ).first()
    
    if evaluacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta postulación ya tiene una evaluación física registrada"
        )
    
    # 4. Convertir tiempo de string a time
    try:
        tiempo_carrera = convertir_tiempo_str_a_time(evaluacion_data.carrera_3200m)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en formato de tiempo de carrera: {str(e)}"
        )
    
    # 5. Crear evaluación física
    nueva_evaluacion = EvaluacionSupervision(
        postulacion_id=evaluacion_data.postulacion_id,
        supervisor_id=current_user.id,
        flexiones=evaluacion_data.flexiones,
        abdominales=evaluacion_data.abdominales,
        carrera_3200m=tiempo_carrera,
        sabe_leer=evaluacion_data.sabe_leer,
        sabe_escribir=evaluacion_data.sabe_escribir,
        sabe_conducir=evaluacion_data.sabe_conducir,
        resultado_psicologico=evaluacion_data.resultado_psicologico,
        resultado_final_supervisor=evaluacion_data.resultado_final_supervisor
    )
    
    db.add(nueva_evaluacion)
    
    # 6. Actualizar estado de la postulación
    # Si no aprueba la evaluación física, marcar como NO_APTO
    if not evaluacion_data.resultado_final_supervisor:
        postulacion.estado = EstadoPostulacion.NO_APTO
    else:
        # Si aprueba, mantener EN_EVALUACION hasta que el jefe dé el veredicto final
        postulacion.estado = EstadoPostulacion.EN_EVALUACION
    
    db.commit()
    db.refresh(nueva_evaluacion)
    
    mensaje = "Evaluación física registrada."
    if evaluacion_data.resultado_final_supervisor:
        mensaje += " El postulante está listo para veredicto final del jefe de unidad."
    else:
        mensaje += " El postulante no es apto físicamente."
    
    return EvaluacionFisicaResponse(
        id=nueva_evaluacion.id,
        mensaje=mensaje
    )


@router.get("/fisica/{postulacion_id}", response_model=EvaluacionFisicaDetalle)
def obtener_evaluacion_fisica(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Obtener Evaluación Física de una postulación**
    
    Muestra los detalles de la evaluación física/supervisión.
    
    Requiere autenticación.
    """
    
    evaluacion = db.query(EvaluacionSupervision).filter(
        EvaluacionSupervision.postulacion_id == postulacion_id
    ).first()
    
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró evaluación física para esta postulación"
        )
    
    return evaluacion

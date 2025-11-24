from app.models.usuario import Usuario, RolUsuario
from app.models.persona import Persona
from app.models.modalidad import Modalidad
from app.models.unidad_reclutamiento import UnidadReclutamiento
from app.models.solicitud_material import SolicitudMaterial
from app.models.tutor import Tutor
from app.models.postulacion import Postulacion, EstadoPostulacion
from app.models.documento_postulante import DocumentoPostulante
from app.models.personal_asignado import PersonalAsignado
from app.models.evaluacion_medica import EvaluacionMedica
from app.models.evaluacion_supervision import EvaluacionSupervision
from app.models.examen_adicional import ExamenAdicional
from app.models.historial_servicio import HistorialServicio
from app.models.tramite import Tramite, TipoTramite, EstadoTramite
from app.models.requisito_tramite import RequisitoTramite

__all__ = [
    "Usuario",
    "RolUsuario",
    "Persona",
    "Modalidad",
    "UnidadReclutamiento",
    "SolicitudMaterial",
    "Tutor",
    "Postulacion",
    "EstadoPostulacion",
    "DocumentoPostulante",
    "PersonalAsignado",
    "EvaluacionMedica",
    "EvaluacionSupervision",
    "ExamenAdicional",
    "HistorialServicio",
    "Tramite",
    "TipoTramite",
    "EstadoTramite",
    "RequisitoTramite",
]

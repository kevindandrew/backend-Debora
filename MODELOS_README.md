# ====================================

# RESUMEN DE MODELOS - Sistema Debora

# ====================================

## MODELOS CREADOS:

### MÓDULO 1: SEGURIDAD Y USUARIOS

- ✅ Usuario (usuarios)
  - Gestión de usuarios del sistema
  - Roles: ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD, MEDICO, SUPERVISOR, LICENCIADO
- ✅ Persona (personas)
  - Datos demográficos centralizados
  - Índices en CI y apellido paterno para búsquedas rápidas

### MÓDULO 2: ADMINISTRACIÓN Y LOGÍSTICA

- ✅ Modalidad (modalidades)
  - Tipos de reclutamiento: Premilitar, Militar, Voluntariado
  - Definición de rangos de edad
- ✅ UnidadReclutamiento (unidades_reclutamiento)
  - Centros de reclutamiento por departamento
  - Capacidad y jefe asignado
- ✅ SolicitudMaterial (solicitudes_material)
  - Pedidos de material de apoyo
  - Estados: PENDIENTE, APROBADO, RECHAZADO

### MÓDULO 3: RECLUTAMIENTO (CORE)

- ✅ Tutor (tutores)
  - Apoderados de menores de edad
- ✅ Postulacion (postulaciones)
  - Inscripciones principales
  - Estados: INSCRITO, EN_EVALUACION, APTO, NO_APTO, LICENCIADO, BAJA
  - Restricción única: persona + gestión
- ✅ DocumentoPostulante (documentos_postulante)
  - Documentos digitalizados (CI, certificados, etc.)

### MÓDULO 4: EVALUACIONES

- ✅ PersonalAsignado (personal_asignado)
  - Médicos y supervisores por unidad
- ✅ EvaluacionMedica (evaluaciones_medicas)
  - Evaluación física completa
  - Características antropométricas
- ✅ EvaluacionSupervision (evaluaciones_supervision)
  - Evaluación física, psicológica y educacional
  - Pruebas: flexiones, abdominales, carrera 3200m
- ✅ ExamenAdicional (examenes_adicionales)
  - ECG, EEG, RX Torax (solo para aptos)
- ✅ HistorialServicio (historial_servicio)
  - Registro de desempeño durante el servicio

### MÓDULO 5: APP MÓVIL Y TRÁMITES

- ✅ Tramite (tramites)
  - Tipos: RECTIFICACION, PERDIDA, CERTIFICACION
  - Estados: SOLICITADO, EN_REVISION, ACEPTADO, RECHAZADO
- ✅ RequisitoTramite (requisitos_tramite)
  - Requisitos específicos por trámite
  - Validación de documentos

## TOTAL: 15 MODELOS + 5 ENUMS

## CARACTERÍSTICAS:

- ✅ Todas las relaciones bidireccionales configuradas
- ✅ Índices en campos de búsqueda frecuente
- ✅ Restricciones de integridad referencial
- ✅ Valores por defecto en campos apropiados
- ✅ Enums tipados para mayor seguridad

## USO:

```python
from app.models import Usuario, Postulacion, EvaluacionMedica, Tramite
# Todos los modelos están disponibles para importar
```

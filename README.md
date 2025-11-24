# 🎖️ API Debora - Sistema de Reclutamiento Militar

API REST completa para el sistema de reclutamiento militar desarrollada con FastAPI y PostgreSQL.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Módulos Implementados](#módulos-implementados)
- [Endpoints Principales](#endpoints-principales)
- [Autenticación](#autenticación)
- [Roles del Sistema](#roles-del-sistema)
- [Ejemplos de Uso](#ejemplos-de-uso)

---

## ✨ Características

- 🔐 **Autenticación JWT** con bcrypt para seguridad
- 👥 **Sistema de roles** (6 roles diferentes con permisos granulares)
- 🏢 **Gestión de unidades** de reclutamiento
- 📅 **Configuración de modalidades** y fechas de inscripción
- 👨‍⚕️ **Evaluaciones médicas y físicas** automatizadas
- 📝 **Trámites en línea** para licenciados
- 🔍 **Búsquedas avanzadas** por CI, apellido, filtros múltiples
- 📚 **Documentación automática** con Swagger UI
- 📁 **Gestión de archivos** (documentos de postulantes, requisitos de trámites)

---

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Base de datos relacional
- **Pydantic** - Validación de datos
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hash de contraseñas
- **Uvicorn** - Servidor ASGI

---

La API estará disponible en:

- **Aplicación:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📁 Estructura del Proyecto

```
backend Debora/
├── app/
│   ├── main.py                 # Aplicación principal
│   ├── config.py               # Configuración
│   ├── database.py             # Conexión a BD
│   ├── security.py             # JWT y bcrypt
│   ├── dependencies.py         # Middleware de autenticación
│   │
│   ├── models/                 # Modelos SQLAlchemy (15 tablas)
│   │   ├── usuario.py
│   │   ├── persona.py
│   │   ├── modalidad.py
│   │   ├── unidad_reclutamiento.py
│   │   ├── postulacion.py
│   │   ├── evaluacion_medica.py
│   │   ├── evaluacion_supervision.py
│   │   ├── tramite.py
│   │   └── ...
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── auth.py
│   │   ├── usuario.py
│   │   ├── modulo2.py
│   │   ├── postulacion.py
│   │   ├── evaluacion.py
│   │   └── tramite.py
│   │
│   ├── routers/                # Endpoints (7 routers)
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── unidades.py
│   │   ├── modalidades.py
│   │   ├── postulaciones.py
│   │   ├── evaluaciones.py
│   │   └── tramites.py
│   │
│   └── utils/                  # Utilidades
│       └── reclutamiento.py
│
├── uploads/                    # Archivos subidos
│   ├── documentos/
│   └── requisitos_tramites/
│
├── .venv/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## � Módulos Implementados

### ✅ Módulo 1: Autenticación y Usuarios

- Login con JWT
- Creación de usuarios administrativos
- Gestión de roles y permisos

### ✅ Módulo 2: Configuración y Unidades

- Crear y gestionar unidades de reclutamiento
- Asignar personal médico y supervisores
- Configurar modalidades (Premilitar, Militar, Voluntariado)
- Establecer fechas de inscripción

### ✅ Módulo 3: Reclutamiento y Postulación

- Registro público de postulantes
- Validación automática de edad según modalidad
- Prevención de doble postulación en misma gestión
- Generación de códigos únicos de inscripción (PM-2025-0001)
- Gestión de tutores para menores de edad
- Subida de documentos digitales
- Búsquedas avanzadas por CI y apellido

### ✅ Módulo 4: Evaluaciones

- Evaluaciones médicas (peso, estatura, grupo sanguíneo, etc.)
- Evaluaciones físicas (flexiones, abdominales, carrera 3200m)
- Veredicto final por jefe de unidad
- Cambios automáticos de estado según resultados
- Flujo: INSCRITO → EN_EVALUACION → APTO/NO_APTO

### ✅ Módulo 5: Trámites y App Móvil

- Solicitud de trámites por licenciados (Rectificación, Pérdida, Certificación)
- Subida de requisitos y documentos
- Respuesta administrativa (aprobar/rechazar)
- Sistema de permisos contextual (licenciados ven solo sus trámites)

---

## 🔌 Endpoints Principales

### Autenticación

| Método | Endpoint             | Descripción               | Auth |
| ------ | -------------------- | ------------------------- | ---- |
| POST   | `/api/v1/auth/login` | Login y obtener token JWT | No   |

### Usuarios

| Método | Endpoint           | Descripción                  | Roles         |
| ------ | ------------------ | ---------------------------- | ------------- |
| POST   | `/api/v1/usuarios` | Crear usuario administrativo | ADMINISTRADOR |
| GET    | `/api/v1/usuarios` | Listar usuarios              | Autenticado   |

### Unidades de Reclutamiento

| Método | Endpoint                         | Descripción      | Roles                                |
| ------ | -------------------------------- | ---------------- | ------------------------------------ |
| POST   | `/api/v1/unidades`               | Crear unidad     | ADMINISTRADOR, DIRECTOR              |
| GET    | `/api/v1/unidades`               | Listar unidades  | ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD |
| POST   | `/api/v1/unidades/{id}/personal` | Asignar personal | ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD |

### Modalidades

| Método | Endpoint                   | Descripción        | Roles                   |
| ------ | -------------------------- | ------------------ | ----------------------- |
| GET    | `/api/v1/modalidades`      | Listar modalidades | Público                 |
| PATCH  | `/api/v1/modalidades/{id}` | Configurar fechas  | ADMINISTRADOR, DIRECTOR |

### Postulaciones

| Método | Endpoint                                    | Descripción          | Roles                                |
| ------ | ------------------------------------------- | -------------------- | ------------------------------------ |
| POST   | `/api/v1/postulaciones`                     | Registrar postulante | Público                              |
| POST   | `/api/v1/postulaciones/{codigo}/documentos` | Subir documentos     | Autenticado                          |
| GET    | `/api/v1/postulaciones`                     | Listar con filtros   | ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD |
| PATCH  | `/api/v1/postulaciones/{id}/veredicto`      | Dar veredicto final  | JEFE_UNIDAD, ADMINISTRADOR           |

### Evaluaciones

| Método | Endpoint                           | Descripción                 | Roles                     |
| ------ | ---------------------------------- | --------------------------- | ------------------------- |
| POST   | `/api/v1/evaluaciones/medica`      | Registrar evaluación médica | MEDICO, ADMINISTRADOR     |
| POST   | `/api/v1/evaluaciones/fisica`      | Registrar evaluación física | SUPERVISOR, ADMINISTRADOR |
| GET    | `/api/v1/evaluaciones/medica/{id}` | Ver evaluación médica       | Autenticado               |
| GET    | `/api/v1/evaluaciones/fisica/{id}` | Ver evaluación física       | Autenticado               |

### Trámites

| Método | Endpoint                           | Descripción       | Roles                     |
| ------ | ---------------------------------- | ----------------- | ------------------------- |
| POST   | `/api/v1/tramites`                 | Solicitar trámite | LICENCIADO, ADMINISTRADOR |
| POST   | `/api/v1/tramites/{id}/requisitos` | Subir requisito   | LICENCIADO, ADMINISTRADOR |
| PATCH  | `/api/v1/tramites/{id}/respuesta`  | Responder trámite | ADMINISTRADOR, DIRECTOR   |
| GET    | `/api/v1/tramites`                 | Listar trámites   | LICENCIADO, ADMINISTRADOR |

**Total: 27 endpoints funcionales**

---

## 🔐 Autenticación

### Login

**Request:**

```json
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "rol": "ADMINISTRADOR",
  "usuario_id": 1
}
```

### Usar el token

En Swagger UI:

1. Click en el botón **"Authorize"** 🔒
2. Ingresa: `Bearer {tu_token}`
3. Click en "Authorize"

En peticiones HTTP:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## � Roles del Sistema

| Rol               | Descripción             | Acceso                               |
| ----------------- | ----------------------- | ------------------------------------ |
| **ADMINISTRADOR** | Acceso total al sistema | Todos los endpoints                  |
| **DIRECTOR**      | Gestión estratégica     | Unidades, modalidades, trámites      |
| **JEFE_UNIDAD**   | Gestión de su unidad    | Asignar personal, veredictos finales |
| **MEDICO**        | Evaluaciones médicas    | Registrar evaluaciones médicas       |
| **SUPERVISOR**    | Evaluaciones físicas    | Registrar evaluaciones físicas       |
| **LICENCIADO**    | App móvil               | Solicitar trámites, ver sus datos    |

---

## 🎯 Ejemplos de Uso

### 1. Registrar Postulante (Público)

```json
POST /api/v1/postulaciones

{
  "ci": "88997766",
  "nombres": "Juan",
  "paterno": "Perez",
  "materno": "Lopez",
  "fecha_nacimiento": "2007-05-20",
  "genero": "M",
  "direccion": "Av. 6 de Agosto #123",
  "modalidad_id": 1,
  "unidad_id": 5,
  "tutor": {
    "nombre_completo": "Mario Perez Garcia",
    "ci": "11223344",
    "relacion": "Padre"
  }
}
```

**Response:**

```json
{
  "codigo_inscripcion": "PM-2025-0001",
  "estado": "INSCRITO",
  "mensaje": "Postulación registrada. Proceda a subir documentos."
}
```

### 2. Evaluación Médica

```json
POST /api/v1/evaluaciones/medica
Authorization: Bearer {token_medico}

{
  "postulacion_id": 1,
  "peso": 65.5,
  "estatura": 1.75,
  "grupo_sanguineo": "O+",
  "observaciones": "Apto físicamente",
  "resultado_apto": true
}
```

### 3. Solicitar Trámite (Licenciado)

```json
POST /api/v1/tramites
Authorization: Bearer {token_licenciado}

{
  "tipo_tramite": "RECTIFICACION",
  "descripcion": "Mi apellido está mal escrito, dice Peres y es Perez."
}
```

---

## � Seguridad

- ✅ Contraseñas hasheadas con **bcrypt**
- ✅ Autenticación con **JWT** (tokens con expiración)
- ✅ Validación de roles por endpoint
- ✅ Protección contra SQL injection (SQLAlchemy ORM)
- ✅ Validación de datos con Pydantic
- ✅ CORS configurado
- ✅ Validación de archivos subidos (extensión y tamaño)

---

## 📁 Gestión de Archivos

### Archivos locales (Implementación actual)

Los archivos se almacenan en:

- `uploads/documentos/` - Documentos de postulantes
- `uploads/requisitos_tramites/` - Requisitos de trámites

### Cloudinary (Recomendado para producción)

Para escalar la aplicación, se recomienda usar **Cloudinary** desde el **frontend**:

**Beneficios:**

- ✅ No consume recursos del servidor backend
- ✅ CDN global para carga rápida
- ✅ Transformación de imágenes automática
- ✅ URLs públicas seguras
- ✅ Backup automático

**Flujo recomendado:**

```
Frontend → Cloudinary (upload directo) → Obtiene URL → Backend (guarda URL en BD)
```

Esto permite que el backend solo maneje URLs en vez de archivos físicos.

---

## 🧪 Testing

Accede a la documentación interactiva en:

- http://localhost:8000/docs

Aquí puedes probar todos los endpoints de forma visual con Swagger UI.

---

## � Base de Datos

### Tablas Principales (15 tablas):

- `usuarios` - Usuarios del sistema
- `personas` - Datos demográficos
- `modalidades` - Tipos de servicio (Premilitar, Militar, Voluntariado)
- `unidades_reclutamiento` - Centros de reclutamiento
- `postulaciones` - Inscripciones de postulantes
- `tutores` - Tutores de menores de edad
- `documentos_postulante` - Documentos digitales subidos
- `personal_asignado` - Médicos y supervisores asignados
- `evaluaciones_medicas` - Exámenes médicos
- `evaluaciones_supervision` - Evaluaciones físicas
- `tramites` - Solicitudes de licenciados
- `requisitos_tramite` - Documentos de trámites
- Y más...

### Enums:

- `rol_usuario` - 6 roles
- `estado_postulacion` - 6 estados
- `tipo_tramite` - 3 tipos
- `estado_tramite` - 4 estados

---

## 🚀 Despliegue

### Producción

1. **Cambiar SECRET_KEY** en `config.py`
2. **Configurar variables de entorno** para producción
3. **Usar PostgreSQL** en servidor dedicado
4. **Configurar HTTPS** (certificado SSL)
5. **Usar Gunicorn** en vez de Uvicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
6. **Configurar Cloudinary** para archivos (recomendado)
7. **Implementar rate limiting** (opcional)
8. **Configurar CORS** con dominios específicos

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

---

## 📄 Licencia

Este proyecto es privado y confidencial.

---

## � Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.

---

## � Estadísticas del Proyecto

- **Endpoints:** 27
- **Modelos:** 15 tablas
- **Schemas:** 40+
- **Routers:** 7
- **Roles:** 6
- **Líneas de código:** ~3500+

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025  
**Estado:** ✅ Producción Ready

---

**Desarrollado con ❤️ usando FastAPI + PostgreSQL + SQLAlchemy**

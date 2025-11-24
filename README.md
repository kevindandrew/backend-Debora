# 🎖️ API Debora - Sistema de Reclutamiento Militar

API REST para el sistema de reclutamiento militar desarrollada con FastAPI y PostgreSQL.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Módulos Implementados](#módulos-implementados)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

## ✨ Características

- 🔐 **Autenticación JWT** con bcrypt
- 👥 **Sistema de roles** (Administrador, Director, Jefe Unidad, Médico, Supervisor, Licenciado)
- 🏢 **Gestión de unidades** de reclutamiento
- 📅 **Configuración de modalidades** y fechas de inscripción
- 👨‍⚕️ **Asignación de personal** médico y supervisores
- 📝 **Validaciones completas** en todos los endpoints
- 📚 **Documentación automática** con Swagger UI

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

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd "backend Debora"
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

```bash
# Crear la base de datos en PostgreSQL
psql -U postgres
CREATE DATABASE Debora;
\q

# Ejecutar el script SQL de la estructura de la base de datos
psql -U postgres -d Debora -f estructura_db.sql
```

---

## ⚙️ Configuración

### Variables de entorno

Edita `app/config.py` o crea un archivo `.env`:

```env
# JWT
SECRET_KEY=tu_clave_secreta_super_segura_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=postgresql://postgres:tu_password@localhost/Debora
```

### Crear usuario administrador inicial

Ejecuta este SQL en tu base de datos:

```sql
-- El password es "admin123"
INSERT INTO usuarios (username, password_hash, rol, estado)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYTQOkpR53S', 'ADMINISTRADOR', true);

INSERT INTO personas (ci, nombres, paterno, materno, fecha_nacimiento, genero, usuario_id)
VALUES ('0000000', 'Administrador', 'Sistema', 'Debora', '1990-01-01', 'M',
        (SELECT id FROM usuarios WHERE username = 'admin'));
```

---

## 🏃 Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

- **Aplicación:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### ⏳ Módulo 5: App Móvil y Trámites

_Próximamente_

---

## 🔌 Endpoints

### Autenticación

| Método | Endpoint             | Descripción               | Auth |
| ------ | -------------------- | ------------------------- | ---- |
| POST   | `/api/v1/auth/login` | Login y obtener token JWT | No   |

### Usuarios

| Método | Endpoint           | Descripción                  | Roles         |
| ------ | ------------------ | ---------------------------- | ------------- |
| POST   | `/api/v1/usuarios` | Crear usuario administrativo | ADMINISTRADOR |
| GET    | `/api/v1/usuarios` | Listar usuarios              | -             |

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
| GET    | `/api/v1/modalidades/{id}` | Ver modalidad      | Público                 |
| PATCH  | `/api/v1/modalidades/{id}` | Configurar fechas  | ADMINISTRADOR, DIRECTOR |

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

## 📁 Estructura del Proyecto

```
backend Debora/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal
│   ├── config.py               # Configuración
│   ├── database.py             # Configuración de DB
│   ├── security.py             # JWT y bcrypt
│   ├── dependencies.py         # Dependencias de auth
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── persona.py
│   │   ├── modalidad.py
│   │   ├── unidad_reclutamiento.py
│   │   ├── postulacion.py
│   │   └── ...
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── usuario.py
│   │   └── modulo2.py
│   │
│   └── routers/                # Endpoints
│       ├── __init__.py
│       ├── auth.py
│       ├── usuarios.py
│       ├── unidades.py
│       └── modalidades.py
│
├── .venv/                      # Entorno virtual
├── .gitignore
├── requirements.txt            # Dependencias
└── README.md
```

---

## 🎯 Ejemplos de Uso

### Crear una unidad de reclutamiento

```json
POST /api/v1/unidades
Authorization: Bearer {token_admin}

{
  "nombre": "Regimiento Colorados",
  "departamento": "La Paz",
  "direccion_fisica": "Calle Calama s/n",
  "capacidad_maxima": 200,
  "jefe_unidad_id": 2
}
```

### Asignar un médico a una unidad

```json
POST /api/v1/unidades/1/personal
Authorization: Bearer {token_admin}

{
  "usuario_id": 3,
  "rol_en_unidad": "MEDICO",
  "gestion": 2025
}
```

### Configurar fechas de inscripción

```json
PATCH /api/v1/modalidades/1
Authorization: Bearer {token_admin}

{
  "fecha_inicio_inscripcion": "2025-01-15",
  "fecha_fin_inscripcion": "2025-02-28"
}
```

---

## 👥 Roles del Sistema

| Rol               | Descripción                         |
| ----------------- | ----------------------------------- |
| **ADMINISTRADOR** | Acceso total al sistema             |
| **DIRECTOR**      | Gestión de unidades y configuración |
| **JEFE_UNIDAD**   | Gestión de su unidad asignada       |
| **MEDICO**        | Evaluaciones médicas                |
| **SUPERVISOR**    | Evaluaciones físicas/psicológicas   |
| **LICENCIADO**    | Trámites en app móvil               |

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con **bcrypt**
- ✅ Autenticación con **JWT** (tokens con expiración)
- ✅ Validación de roles por endpoint
- ✅ Protección contra SQL injection (SQLAlchemy ORM)
- ✅ Validación de datos con Pydantic
- ✅ CORS configurado

---

## 🧪 Testing

Accede a la documentación interactiva en:

- http://localhost:8000/docs

Aquí puedes probar todos los endpoints de forma visual.

---

## 📝 Base de Datos

La estructura completa de la base de datos incluye:

### Tablas Principales:

- `usuarios` - Usuarios del sistema
- `personas` - Datos demográficos
- `modalidades` - Tipos de servicio
- `unidades_reclutamiento` - Centros de reclutamiento
- `postulaciones` - Inscripciones
- `evaluaciones_medicas` - Exámenes médicos
- `evaluaciones_supervision` - Evaluaciones físicas
- `tramites` - Solicitudes de licenciados

### Enums:

- `rol_usuario`
- `estado_postulacion`
- `tipo_tramite`
- `estado_tramite`

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

## 👨‍💻 Desarrolladores

Sistema desarrollado para la gestión de reclutamiento militar.

---

## 📞 Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025

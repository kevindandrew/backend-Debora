from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, auth, unidades, modalidades, postulaciones, evaluaciones, tramites

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Debora - Sistema de Reclutamiento",
    description="API para el sistema de reclutamiento militar",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
# Módulo 1: Autenticación y Usuarios
app.include_router(auth.router)
app.include_router(usuarios.router)

# Módulo 2: Configuración y Unidades
app.include_router(unidades.router)
app.include_router(modalidades.router)

# Módulo 3: Reclutamiento
app.include_router(postulaciones.router)

# Módulo 4: Evaluaciones
app.include_router(evaluaciones.router)

# Módulo 5: Trámites
app.include_router(tramites.router)

# Endpoint raíz
@app.get("/")
def root():
    return {
        "message": "API Debora - Sistema de Reclutamiento",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "✅ Operativo",
        "modulos": {
            "modulo_1": "✅ Autenticación y Usuarios",
            "modulo_2": "✅ Configuración y Unidades",
            "modulo_3": "✅ Reclutamiento y Postulación",
            "modulo_4": "✅ Evaluaciones Médicas y Físicas",
            "modulo_5": "✅ Trámites y App Móvil"
        }
    }

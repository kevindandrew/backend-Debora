from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, auth, unidades, modalidades, postulaciones, evaluaciones, tramites, materiales

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Debora - Sistema de Reclutamiento",
    description="API para el sistema de reclutamiento militar",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(unidades.router)
app.include_router(modalidades.router)
app.include_router(postulaciones.router)
app.include_router(evaluaciones.router)
app.include_router(tramites.router)
app.include_router(materiales.router)

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios

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
app.include_router(usuarios.router)

# Endpoint raíz
@app.get("/")
def root():
    return {
        "message": "API Debora - Sistema de Reclutamiento",
        "version": "1.0.0",
        "docs": "/docs"
    }

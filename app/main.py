from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, auth, unidades, modalidades, postulaciones, evaluaciones, tramites, materiales, estadisticas, auditoria
from fastapi import Request
import time

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Debora - Sistema de Reclutamiento",
    description="API para el sistema de reclutamiento militar",
    version="1.0.0"
)

# Middleware de Logging (Auditoría simple en archivo)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Formato: FECHA | METODO | URL | STATUS | TIEMPO
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {request.method} | {request.url.path} | {response.status_code} | {process_time:.4f}s\n"
    
    try:
        with open("audit.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass # No fallar si no se puede escribir el log
        
    return response

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
app.include_router(estadisticas.router)
app.include_router(auditoria.router)

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

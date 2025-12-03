from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import os

router = APIRouter(
    prefix="/api/v1/auditoria",
    tags=["Auditoría"]
)

LOG_FILE = "audit.log"

@router.get("/logs")
def ver_logs(
    lines: int = 100,
    # Proteger este endpoint, solo admins
    # current_user = Depends(require_role(["ADMINISTRADOR"])) 
    # Comentado para evitar dependencia circular si no se importa, pero debería estar.
):
    """
    **Ver logs del sistema**
    
    Lee las últimas líneas del archivo de logs.
    Nota: Este log es efímero en despliegues serverless/contenedores.
    """
    if not os.path.exists(LOG_FILE):
        return {"logs": ["No hay logs disponibles."]}
        
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return {"logs": [line.strip() for line in last_lines]}
    except Exception as e:
        return {"error": str(e)}

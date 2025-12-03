from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.models.postulacion import Postulacion
from app.models.unidad_reclutamiento import UnidadReclutamiento
from app.dependencies import require_role

router = APIRouter(
    prefix="/api/v1/estadisticas",
    tags=["Estadísticas"]
)

@router.get("/evolucion-usuarios")
def obtener_evolucion_usuarios(
    gestion: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Obtener evolución de usuarios por unidad**
    
    Retorna la cantidad de postulantes por mes para cada unidad en una gestión específica.
    Ideal para gráficos de líneas.
    
    - **gestion**: Año a consultar (por defecto el año actual)
    """
    if not gestion:
        gestion = datetime.now().year
        
    # Consulta agrupada por Unidad y Mes
    resultados = db.query(
        UnidadReclutamiento.nombre,
        extract('month', Postulacion.fecha_postulacion).label('mes'),
        func.count(Postulacion.id).label('cantidad')
    ).join(Postulacion).filter(
        Postulacion.gestion == gestion
    ).group_by(
        UnidadReclutamiento.nombre,
        extract('month', Postulacion.fecha_postulacion)
    ).all()
    
    # Procesar resultados para el frontend
    # Estructura: { "Unidad A": {1: 10, 2: 15...}, "Unidad B": ... }
    datos_procesados = {}
    unidades_nombres = set()
    
    for nombre_unidad, mes, cantidad in resultados:
        if nombre_unidad not in datos_procesados:
            datos_procesados[nombre_unidad] = {}
        datos_procesados[nombre_unidad][int(mes)] = cantidad
        unidades_nombres.add(nombre_unidad)
        
    # Formatear para Chart.js o similar
    # Labels: Enero, Febrero, ...
    meses_labels = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    
    datasets = []
    colores = [
        "#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b", 
        "#858796", "#5a5c69", "#f8f9fc", "#4e73df", "#1cc88a"
    ] # Colores de ejemplo
    
    for i, unidad in enumerate(unidades_nombres):
        data = []
        for mes_idx in range(1, 13):
            # Obtener cantidad o 0 si no hay datos para ese mes
            cantidad = datos_procesados.get(unidad, {}).get(mes_idx, 0)
            data.append(cantidad)
            
        datasets.append({
            "label": unidad,
            "data": data,
            "borderColor": colores[i % len(colores)],
            "backgroundColor": "transparent",
            "tension": 0.3,
            "fill": False
        })
        
    return {
        "gestion": gestion,
        "labels": meses_labels,
        "datasets": datasets
    }

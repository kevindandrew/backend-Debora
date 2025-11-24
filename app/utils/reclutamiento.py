"""
Utilidades para el Módulo 3: Reclutamiento
"""
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.postulacion import Postulacion

def calcular_edad(fecha_nacimiento: date) -> int:
    """Calcular la edad de una persona"""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad

def generar_codigo_inscripcion(db: Session, modalidad_nombre: str, gestion: int) -> str:
    """
    Generar código único de inscripción
    Formato: {PREFIJO}-{GESTION}-{NUMERO}
    Ejemplos: PM-2025-0001, ML-2025-0023, VL-2025-0100
    """
    # Determinar prefijo según modalidad
    prefijos = {
        "Premilitar": "PM",
        "Militar": "ML",
        "Voluntariado": "VL"
    }
    
    prefijo = prefijos.get(modalidad_nombre, "XX")
    
    # Contar postulaciones existentes de esta modalidad en esta gestión
    # para generar el número secuencial
    count = db.query(Postulacion).filter(
        Postulacion.gestion == gestion,
        Postulacion.codigo_inscripcion.like(f"{prefijo}-{gestion}-%")
    ).count()
    
    # Generar nuevo número
    numero = count + 1
    
    # Formato: PM-2025-0001
    codigo = f"{prefijo}-{gestion}-{numero:04d}"
    
    # Verificar que no exista (por si acaso)
    while db.query(Postulacion).filter(Postulacion.codigo_inscripcion == codigo).first():
        numero += 1
        codigo = f"{prefijo}-{gestion}-{numero:04d}"
    
    return codigo

def validar_edad_modalidad(edad: int, edad_minima: int, edad_maxima: int) -> tuple[bool, str]:
    """
    Validar si la edad está en el rango permitido para la modalidad
    Retorna: (es_valido, mensaje_error)
    """
    if edad < edad_minima:
        return False, f"Edad mínima requerida: {edad_minima} años. Edad actual: {edad} años"
    
    if edad > edad_maxima:
        return False, f"Edad máxima permitida: {edad_maxima} años. Edad actual: {edad} años"
    
    return True, ""

def es_menor_de_edad(edad: int) -> bool:
    """Verificar si es menor de 18 años"""
    return edad < 18

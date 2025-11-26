from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(
    prefix="/api/v1/fix-constraint",
    tags=["Fix DB"],
)

@router.get("/")
def fix_constraint(db: Session = Depends(get_db)):
    try:
        # 1. Eliminar la restricción existente
        db.execute(text("ALTER TABLE personal_asignado DROP CONSTRAINT IF EXISTS personal_asignado_rol_en_unidad_check;"))
        
        # 2. Volver a crear la restricción con los valores correctos
        # Asegúrate de incluir TODOS los roles que deben ser válidos
        db.execute(text("""
            ALTER TABLE personal_asignado 
            ADD CONSTRAINT personal_asignado_rol_en_unidad_check 
            CHECK (rol_en_unidad IN ('MEDICO', 'SUPERVISOR', 'JEFE_UNIDAD'));
        """))
        
        db.commit()
        return {"message": "Restricción actualizada correctamente. Ahora se permite JEFE_UNIDAD."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la restricción: {str(e)}")

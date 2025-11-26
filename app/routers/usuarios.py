from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.models.persona import Persona
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioCreateResponse
from app.security import get_password_hash
from app.dependencies import require_role

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"]
)

@router.get("/", response_model=List[UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    """
    **Obtener todos los usuarios**
    
    Endpoint GET básico para listar todos los usuarios del sistema.
    """
    usuarios = db.query(Usuario).all()
    
    response = []
    for u in usuarios:
        # Obtener la primera persona asociada (asumiendo 1:1 o 1:N donde importa la primera)
        persona = u.personas[0] if u.personas else None
        
        response.append(UsuarioResponse(
            id=u.id,
            username=u.username,
            rol=u.rol.value if hasattr(u.rol, 'value') else str(u.rol),
            fecha_creacion=u.fecha_creacion,
            estado=u.estado,
            nombres=persona.nombres if persona else None,
            paterno=persona.paterno if persona else None,
            materno=persona.materno if persona else None
        ))
    
    return response

@router.post("/", response_model=UsuarioCreateResponse)
def crear_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "JEFE_UNIDAD"]))
):
    """
    **Crear usuario administrativo (Solo ADMINISTRADOR)**
    
    Crea un nuevo usuario en el sistema con su persona asociada.
    
    Requiere rol: ADMINISTRADOR
    
    - **username**: Nombre de usuario único
    - **password**: Contraseña (se hasheará con bcrypt)
    - **rol**: Rol del usuario (ADMINISTRADOR, DIRECTOR, JEFE_UNIDAD, MEDICO, SUPERVISOR, LICENCIADO)
    - **nombres**: Nombres de la persona
    - **paterno**: Apellido paterno
    - **materno**: Apellido materno (opcional)
    - **ci**: Carnet de identidad único
    """
    
    # Validar que el username no exista
    existing_user = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El username '{usuario_data.username}' ya existe"
        )
    
    # Validar que el CI no exista
    existing_persona = db.query(Persona).filter(Persona.ci == usuario_data.ci).first()
    if existing_persona:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El CI '{usuario_data.ci}' ya está registrado"
        )
    
    # Validar que el rol sea válido
    try:
        rol_enum = RolUsuario(usuario_data.rol)
    except ValueError:
        roles_validos = [r.value for r in RolUsuario]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Roles válidos: {', '.join(roles_validos)}"
        )
    
    # Crear usuario
    nuevo_usuario = Usuario(
        username=usuario_data.username,
        password_hash=get_password_hash(usuario_data.password),
        rol=rol_enum,
        estado=True
    )
    
    db.add(nuevo_usuario)
    db.flush()  # Para obtener el ID del usuario
    
    # Crear persona asociada (sin fecha de nacimiento por ahora, ajustar según necesites)
    nueva_persona = Persona(
        ci=usuario_data.ci,
        nombres=usuario_data.nombres,
        paterno=usuario_data.paterno,
        materno=usuario_data.materno,
        fecha_nacimiento=date(1990, 1, 1),  # Valor por defecto, ajustar después
        genero='M',  # Valor por defecto, ajustar después
        usuario_id=nuevo_usuario.id
    )
    
    db.add(nueva_persona)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return UsuarioCreateResponse(
        id=nuevo_usuario.id,
        username=nuevo_usuario.username,
        mensaje="Usuario creado exitosamente"
    )

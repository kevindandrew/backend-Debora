from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.models.persona import Persona
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioCreateResponse, UsuarioUpdateMe, UsuarioUpdateAdmin
from app.security import get_password_hash
from app.dependencies import require_role, get_current_user

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"]
)

@router.get("/", response_model=List[UsuarioResponse])
def obtener_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Obtener todos los usuarios**
    
    Endpoint GET básico para listar todos los usuarios del sistema.
    Requiere rol: ADMINISTRADOR o DIRECTOR
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
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Crear usuario administrativo**
    
    Crea un nuevo usuario en el sistema con su persona asociada.
    
    Requiere rol: ADMINISTRADOR o DIRECTOR
    
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

@router.put("/me", response_model=UsuarioResponse)
def actualizar_mi_perfil(
    usuario_update: UsuarioUpdateMe,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Actualizar mi propio perfil**
    
    Permite al usuario logueado actualizar su información básica.
    """
    # Actualizar password si se proporciona
    if usuario_update.password:
        current_user.password_hash = get_password_hash(usuario_update.password)
    
    # Actualizar datos de persona
    persona = current_user.personas[0] if current_user.personas else None
    if persona:
        if usuario_update.nombres:
            persona.nombres = usuario_update.nombres
        if usuario_update.paterno:
            persona.paterno = usuario_update.paterno
        if usuario_update.materno:
            persona.materno = usuario_update.materno
        
        db.add(persona)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # Reconstruir respuesta
    persona = current_user.personas[0] if current_user.personas else None
    return UsuarioResponse(
        id=current_user.id,
        username=current_user.username,
        rol=current_user.rol.value if hasattr(current_user.rol, 'value') else str(current_user.rol),
        fecha_creacion=current_user.fecha_creacion,
        estado=current_user.estado,
        nombres=persona.nombres if persona else None,
        paterno=persona.paterno if persona else None,
        materno=persona.materno if persona else None
    )

@router.put("/{user_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    user_id: int,
    usuario_update: UsuarioUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMINISTRADOR", "DIRECTOR"]))
):
    """
    **Actualizar usuario (Admin/Director)**
    
    Permite actualizar cualquier información de un usuario.
    Requiere rol: ADMINISTRADOR o DIRECTOR
    """
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar username único si cambia
    if usuario_update.username and usuario_update.username != usuario.username:
        existing_user = db.query(Usuario).filter(Usuario.username == usuario_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El username '{usuario_update.username}' ya existe"
            )
        usuario.username = usuario_update.username
        
    # Actualizar password
    if usuario_update.password:
        usuario.password_hash = get_password_hash(usuario_update.password)
        
    # Actualizar rol
    if usuario_update.rol:
        try:
            rol_enum = RolUsuario(usuario_update.rol)
            usuario.rol = rol_enum
        except ValueError:
            roles_validos = [r.value for r in RolUsuario]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol inválido. Roles válidos: {', '.join(roles_validos)}"
            )
            
    # Actualizar estado
    if usuario_update.estado is not None:
        usuario.estado = usuario_update.estado
        
    # Actualizar datos de persona
    persona = usuario.personas[0] if usuario.personas else None
    if persona:
        if usuario_update.nombres:
            persona.nombres = usuario_update.nombres
        if usuario_update.paterno:
            persona.paterno = usuario_update.paterno
        if usuario_update.materno:
            persona.materno = usuario_update.materno
        
        # Validar CI único si cambia
        if usuario_update.ci and usuario_update.ci != persona.ci:
            existing_persona = db.query(Persona).filter(Persona.ci == usuario_update.ci).first()
            if existing_persona:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El CI '{usuario_update.ci}' ya está registrado"
                )
            persona.ci = usuario_update.ci
            
        db.add(persona)
        
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    # Reconstruir respuesta
    persona = usuario.personas[0] if usuario.personas else None
    return UsuarioResponse(
        id=usuario.id,
        username=usuario.username,
        rol=usuario.rol.value if hasattr(usuario.rol, 'value') else str(usuario.rol),
        fecha_creacion=usuario.fecha_creacion,
        estado=usuario.estado,
        nombres=persona.nombres if persona else None,
        paterno=persona.paterno if persona else None,
        materno=persona.materno if persona else None
    )

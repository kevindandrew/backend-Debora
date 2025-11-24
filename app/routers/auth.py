from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, LoginResponse
from app.security import verify_password, create_access_token

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    **Autenticación de usuarios**
    
    Valida las credenciales y devuelve un token JWT para acceder a los endpoints protegidos.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna:
    - **access_token**: Token JWT
    - **token_type**: Tipo de token (bearer)
    - **rol**: Rol del usuario
    - **usuario_id**: ID del usuario
    """
    # Buscar usuario por username
    user = db.query(Usuario).filter(Usuario.username == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not user.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador",
        )
    
    # Crear token JWT
    access_token = create_access_token(
        data={
            "sub": user.username,
            "rol": user.rol.value,
            "usuario_id": user.id
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        rol=user.rol.value,
        usuario_id=user.id
    )

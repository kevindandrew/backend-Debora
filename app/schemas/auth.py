from pydantic import BaseModel

# Schema para Login Request
class LoginRequest(BaseModel):
    username: str
    password: str

# Schema para Login Response
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    rol: str
    usuario_id: int

# Schema para Token Data
class TokenData(BaseModel):
    username: str
    rol: str
    usuario_id: int

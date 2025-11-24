from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str = "tu_clave_secreta_super_segura_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:150415kyb@localhost/Debora"
    
    class Config:
        env_file = ".env"

settings = Settings()

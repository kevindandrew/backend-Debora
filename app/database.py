from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:150415kyb@localhost/Debora"

# Crear el engine de SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear SessionLocal para las transacciones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

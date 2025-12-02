print("Script started")
import sys
import os
from sqlalchemy.orm import Session

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models.usuario import Usuario, RolUsuario
from app.models.persona import Persona
from app.security import get_password_hash
from app.main import app
from fastapi.testclient import TestClient
from datetime import date

def verify_director_permissions():
    print("Starting verification for DIRECTOR role...")
    
    db = SessionLocal()
    client = TestClient(app)
    
    try:
        # 1. Create Director User
        username = "director_test"
        password = "password123"
        
        # Check if user exists
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if user:
            print(f"User {username} already exists. Updating role to DIRECTOR...")
            user.rol = RolUsuario.DIRECTOR
            user.password_hash = get_password_hash(password)
            db.commit()
        else:
            print(f"Creating user {username} with role DIRECTOR...")
            new_user = Usuario(
                username=username,
                password_hash=get_password_hash(password),
                rol=RolUsuario.DIRECTOR,
                estado=True
            )
            db.add(new_user)
            db.flush()
            
            # Create associated Persona
            new_persona = Persona(
                ci="9999999",
                nombres="Director",
                paterno="Test",
                fecha_nacimiento=date(1980, 1, 1),
                genero="M",
                usuario_id=new_user.id
            )
            db.add(new_persona)
            db.commit()
            print(f"User {username} created.")

        # 2. Login
        print("Logging in...")
        response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
        
        # 3. Test GET /api/v1/usuarios (Admin/Director only)
        print("Testing GET /api/v1/usuarios...")
        response = client.get("/api/v1/usuarios/", headers=headers)
        if response.status_code == 200:
            print("✅ GET /api/v1/usuarios success!")
        else:
            print(f"❌ GET /api/v1/usuarios failed: {response.status_code} - {response.text}")

        # 4. Test POST /api/v1/usuarios (Admin/Director only)
        print("Testing POST /api/v1/usuarios (Create User)...")
        new_user_data = {
            "username": "new_user_by_director",
            "password": "password123",
            "rol": "MEDICO",
            "nombres": "New",
            "paterno": "User",
            "ci": "8888888"
        }
        
        # Clean up if exists
        existing = db.query(Usuario).filter(Usuario.username == new_user_data["username"]).first()
        if existing:
            db.delete(existing) # This might fail due to FK, but let's try
            db.commit()
            
        response = client.post("/api/v1/usuarios/", json=new_user_data, headers=headers)
        if response.status_code == 200:
            print("✅ POST /api/v1/usuarios success!")
        else:
            print(f"❌ POST /api/v1/usuarios failed: {response.status_code} - {response.text}")

        # 5. Test GET /api/v1/postulaciones (Admin/Director see all)
        print("Testing GET /api/v1/postulaciones...")
        response = client.get("/api/v1/postulaciones/", headers=headers)
        if response.status_code == 200:
            print("✅ GET /api/v1/postulaciones success!")
        else:
            print(f"❌ GET /api/v1/postulaciones failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_director_permissions()

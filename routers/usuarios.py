from fastapi import APIRouter, HTTPException
from models import LoginRequest
from configurations import alumnos_collection, profesores_collection, admins_collection
from bson.objectid import ObjectId
from datetime import datetime
from passlib.context import CryptContext
import jwt 

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "3244"

def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/api/login")
async def logear_usuario(login: LoginRequest):
    try:
        usuario = alumnos_collection.find_one({"email": login.email}) or \
                  profesores_collection.find_one({"email": login.email}) or \
                  admins_collection.find_one({"email": login.email})

        print(usuario)  

        if not usuario:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        
        if not verify_password(login.password, usuario["password"]):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
    
        token_data = {
            "email": usuario["email"], 
            "nombre": usuario["nombre"], 
            "rol": usuario["rol"],
            "plan": usuario.get("plan", "basico"),
            "id": str(usuario["_id"])  
        }
        token = create_jwt_token(token_data)
        
        return {"status_code": 200, "message": "Login exitoso", "token": token, "user": usuario["nombre"], "plan": token_data["plan"], "id": token_data["id"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
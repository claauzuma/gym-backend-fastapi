from fastapi import APIRouter, HTTPException
from models import Profesor
from configurations import profesores_collection,clases_collection
from bson.objectid import ObjectId
from datetime import datetime
from passlib.context import CryptContext

router = APIRouter()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password):
    return pwd_context.hash(plain_password)


@router.get("/api/profesores")
async def get_all_profesores():
    data = profesores_collection.find()
    return [convert_object_id(profesor) for profesor in data]

@router.get("/api/profesores/{profesor_id}")
async def get_profesor_by_id(profesor_id: str):
    try:
        id = ObjectId(profesor_id)
        profesor = profesores_collection.find_one({"_id": id})
        if not profesor:
            raise HTTPException(status_code=404, detail="Profesor noo encontrado")
        return convert_object_id(profesor)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de ID invalido")

@router.post('/api/profesores')
async def create_profesor(new_profesor: Profesor):
    try:
        hashed_password = hash_password(new_profesor.password)
        new_profesor_dict = dict(new_profesor)
        new_profesor_dict['password'] = hashed_password

        resp = profesores_collection.insert_one(new_profesor_dict)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    

@router.put("/api/profesores/{profesor_id}")
async def update_profesor(profesor_id: str, updated_profesor: Profesor):
    try:
        id = ObjectId(profesor_id)
        existing_doc = profesores_collection.find_one({"_id": id})
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Profesor no existe")
        updated_profesor.updated_at = datetime.now()
        resp = profesores_collection.update_one({"_id": id}, {"$set": updated_profesor.dict(exclude_unset=True)})
        if resp.modified_count == 0:
            raise HTTPException(status_code=500, detail="Error en actualizar profe")
        return {"status_code": 200, "message": "Profesor agregado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.delete("/api/profesores/{profesor_id}")
async def delete_profesor(profesor_id: str):
    try:
        id = ObjectId(profesor_id)
        profesor = profesores_collection.find_one({"_id": id})
        if not profesor:
            raise HTTPException(status_code=404, detail="Profesor noo encontrado")
        
        clases_asociadas = clases_collection.find({"emailProfesor": profesor.get("email")})
        for clase in clases_asociadas:
            clases_collection.delete_one({"_id": clase["_id"]})

        resp = profesores_collection.delete_one({"_id": id})
        if resp.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Error en borrar al profesor")
        return {"status_code": 200, "message": "Profesor eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

def convert_object_id(profesor: dict) -> dict:
    profesor["_id"] = str(profesor["_id"])
    return profesor

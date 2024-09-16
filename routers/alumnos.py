from fastapi import APIRouter, HTTPException
from models import Alumno
from configurations import alumnos_collection,rutinas_collection,clases_collection
from bson.objectid import ObjectId
from datetime import datetime

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def hash_password(plain_password):
    return pwd_context.hash(plain_password)

@router.get("/api/alumnos")
async def get_all_alumnos():
    data = alumnos_collection.find()
    return [convert_object_id(alumno) for alumno in data]

@router.get("/api/alumnos/{alumno_id}")
async def get_alumno_by_id(alumno_id: str):
    try:
        id = ObjectId(alumno_id)
        alumno = alumnos_collection.find_one({"_id": id})
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno not found")
        return convert_object_id(alumno)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid alumno ID format")

@router.post('/api/alumnos')
async def create_alumno(new_alumno: Alumno):
    try:
        hashed_password = hash_password(new_alumno.password)
        new_alumno_dict = dict(new_alumno)
        new_alumno_dict['password'] = hashed_password

        resp = alumnos_collection.insert_one(new_alumno_dict)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.put("/api/alumnos/{alumno_id}")
async def update_alumno(alumno_id: str, updated_alumno: Alumno):
    try:
        id = ObjectId(alumno_id)
        existing_doc = alumnos_collection.find_one({"_id": id})
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Alumno no existe")
        updated_alumno.updated_at = datetime.now()
        resp = alumnos_collection.update_one({"_id": id}, {"$set": updated_alumno.dict(exclude_unset=True)})
        print(resp)  
        if resp.modified_count == 0:
            raise HTTPException(status_code=500, detail="Error al actualizar alumno")
        return {"status_code": 200, "message": "Alumno actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error :  {e}")

@router.delete("/api/alumnos/{alumno_id}")
async def delete_alumno(alumno_id: str):
    try:
        id = ObjectId(alumno_id)
        alumno = alumnos_collection.find_one({"_id": id})
        

        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
        
        rutinas_collection.delete_many({"nombreAlumno": alumno["nombre"], "dniAlumno": alumno["dni"]})
        clases_collection.update_many({"alumnosInscriptos": alumno_id},{"$pull": {"alumnosInscriptos": alumno_id}}
        )

        resp = alumnos_collection.delete_one({"_id": id})
        if resp.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Error al eliminar alumno")
        return {"status_code": 200, "message": "Alumno eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    
    
@router.post("/api/clases/{clase_id}/inscribir/{alumno_id}")
async def inscribir_alumno(clase_id: str, alumno_id: str):
    try:

        alumno = alumnos_collection.find_one({"_id": ObjectId(alumno_id)})
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")

        clase = clases_collection.find_one({"_id": ObjectId(clase_id)})
        if not clase:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
       
        if alumno_id in clase.get("alumnosInscriptos", []):
            raise HTTPException(status_code=400, detail="El alumno ya estaba inscripto")
        
        if "capacidad" in clase and len(clase.get("alumnosInscriptos", [])) >= clase["capacidad"]:
            raise HTTPException(status_code=400, detail="No hay más cupo disponible en la clase")
        
        clases_collection.update_one(
            {"_id": ObjectId(clase_id)},
            {"$push": {"alumnosInscriptos": alumno_id}}
        )

        return {"status_code": 200, "message": f"Alumno {alumno_id} inscrito a la clase {clase_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")    
    
@router.post("/api/clases/{clase_id}/desinscribir/{alumno_id}")
async def desinscribir_alumno(clase_id: str, alumno_id: str):
    try:
        alumno = alumnos_collection.find_one({"_id": ObjectId(alumno_id)})
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")

        clase = clases_collection.find_one({"_id": ObjectId(clase_id)})
        if not clase:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        
        if alumno_id not in clase.get("alumnosInscriptos", []):
            raise HTTPException(status_code=400, detail=" El alumno no esta inscrito en la clase")

        clases_collection.update_one(
            {"_id": ObjectId(clase_id)},
            {"$pull": {"alumnosInscriptos": alumno_id}}
        )
        return {"status_code": 200, "message": f"Alumno {alumno_id} desinscrito de la clase {clase_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")    

def convert_object_id(alumno: dict) -> dict:
    alumno["_id"] = str(alumno["_id"])
    return alumno

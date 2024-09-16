from fastapi import APIRouter, HTTPException
from models import Clase
from configurations import clases_collection, profesores_collection, alumnos_collection
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/api/clases")
async def get_all_clases():
    try:
        data = clases_collection.find()
        return [convert_object_id(clase) for clase in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.get("/api/clases/{clase_id}")
async def get_clase_by_id(clase_id: str):
    try:
        id = ObjectId(clase_id)
        clase = clases_collection.find_one({"_id": id})
        if not clase:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        return convert_object_id(clase)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de clase inválido")
    
@router.get("/api/clases/{clase_id}/alumnos")
async def get_alumnos_inscriptos(clase_id: str):
    try:

        id = ObjectId(clase_id)
        
        clase = clases_collection.find_one({"_id": id})
        if not clase:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        
        alumnos_ids = clase.get("alumnosInscriptos", [])
        
        if not alumnos_ids:
            return {"status_code": 200, "message": "No hay alumnos inscriptos en esta clase", "alumnos": []}
        
        alumnos = alumnos_collection.find({"_id": {"$in": [ObjectId(alumno_id) for alumno_id in alumnos_ids]}})
        
        alumnos_list = [convert_object_id(alumno) for alumno in alumnos]
        
        return {"status_code": 200, "alumnos": alumnos_list}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.post('/api/clases')
async def create_clase(new_clase: Clase):
    try:
        profesor = profesores_collection.find_one({
            "email": new_clase.emailProfesor,
            "nombre": new_clase.nombreProfesor
        })
        if not profesor:
            raise HTTPException(status_code=400, detail="Profesor no encontraado")

        resp = clases_collection.insert_one(new_clase.dict())
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.put("/api/clases/{clase_id}")
async def update_clase(clase_id: str, updated_clase: Clase):
    try:
        id = ObjectId(clase_id)
        existing_doc = clases_collection.find_one({"_id": id})
        if not existing_doc:
            raise HTTPException(status_code=404, detail="La clase no existe")
        
        if updated_clase.nombreProfesor and updated_clase.emailProfesor:
            profesor = profesores_collection.find_one({
                "nombre": updated_clase.nombreProfesor,
                "email": updated_clase.emailProfesor
            })
            
            if not profesor:
                raise HTTPException(status_code=400, detail="El profesor no existe o el nombre y el email no coinciden")

        resp = clases_collection.update_one({"_id": id}, {"$set": updated_clase.dict(exclude_unset=True)})
        if resp.modified_count == 0:
            raise HTTPException(status_code=500, detail="Se fallo al editar la clase")
        return {"status_code": 200, "message": "Clase updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/api/clases/{clase_id}")
async def delete_clase(clase_id: str):
    try:
        id = ObjectId(clase_id)
        clase = clases_collection.find_one({"_id": id})
        if not clase:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        resp = clases_collection.delete_one({"_id": id})
        if resp.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Se fallo al editar la clase")
        return {"status_code": 200, "message": "Clase borrada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

def convert_object_id(clase: dict) -> dict:
    clase["_id"] = str(clase["_id"])
    return clase

from fastapi import APIRouter, HTTPException
from models import Rutina
from configurations import rutinas_collection, alumnos_collection
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/api/rutinas")
async def get_all_rutinas():
    data = rutinas_collection.find()
    return [convert_object_id(rutina) for rutina in data]

@router.get("/api/rutinas/{rutina_id}")
async def get_rutina_by_id(rutina_id: str):
    try:
        id = ObjectId(rutina_id)
        rutina = rutinas_collection.find_one({"_id": id})
        if not rutina:
            raise HTTPException(status_code=404, detail="Rutina no encontrada")
        return convert_object_id(rutina)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de ID invalido")

@router.post('/api/rutinas')
async def create_rutina(new_rutina: Rutina):
    try:
        alumno = alumnos_collection.find_one({
            "nombre": new_rutina.nombreAlumno,
            "dni": new_rutina.dniAlumno
        })
        
        if not alumno:
            raise HTTPException(status_code=400, detail="Alumno no encontrado")
        
        resp = rutinas_collection.insert_one(dict(new_rutina))
        return {"status_code": 200, "id": str(resp.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
    

@router.put("/api/rutinas/{rutina_id}")
async def update_rutina(rutina_id: str, updated_rutina: Rutina):
    try:
        id = ObjectId(rutina_id)
        existing_doc = rutinas_collection.find_one({"_id": id})
        if not existing_doc:
            raise HTTPException(status_code=404, detail="La rutina no existe")
        
        if updated_rutina.nombreAlumno and updated_rutina.dniAlumno:
            alumno = alumnos_collection.find_one({
                "nombre": updated_rutina.nombreAlumno,
                "dni": updated_rutina.dniAlumno
            })
            
            if not alumno:
                raise HTTPException(status_code=400, detail="El alumno no existe o los datos son incorrectos")
        
        
        resp = rutinas_collection.update_one({"_id": id}, {"$set": updated_rutina.dict(exclude_unset=True)})
        if resp.modified_count == 0:
            raise HTTPException(status_code=500, detail="Error al actualizar rutina")
        return {"status_code": 200, "message": "Rutina actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/api/rutinas/{rutina_id}")
async def delete_rutina(rutina_id: str):
    try:
        id = ObjectId(rutina_id)
        rutina = rutinas_collection.find_one({"_id": id})
        if not rutina:
            raise HTTPException(status_code=404, detail="Rutina not found")
        resp = rutinas_collection.delete_one({"_id": id})
        if resp.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Falla al eliminar rutina")
        return {"status_code": 200, "message": "Rutina eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

def convert_object_id(rutina: dict) -> dict:
    rutina["_id"] = str(rutina["_id"])
    return rutina

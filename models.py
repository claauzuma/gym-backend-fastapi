from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, field_validator
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Usuario(BaseModel):
    nombre: str
    apellido: str
    dni: constr(min_length=8, max_length=8)  # Restricción para tener exactamente 8 caracteres
    email: EmailStr
    password: str  # Campo cambiado a 'password'

    # Validador para el campo 'dni'
    @field_validator('dni')
    def validate_dni_length(cls, v):
        if len(v) != 8:
            raise ValueError('El DNI debe tener exactamente 8 caracteres')
        return v

class Alumno(Usuario):
    ingreso: Optional[datetime] = None
    plan: Optional[str] = None
    rol: str = "alumno" 

class Profesor(Usuario):
    ingreso: Optional[datetime] = None
    rol: str = "profe" 

class Admin(Usuario):
    rol: str = "admin" 

class Rutina(BaseModel):
    idProfesor: str
    descripcion: str
    nombreAlumno: str
    dniAlumno: constr(min_length=8, max_length=8)  
    nivel: Optional[str] = None

    # Validador para el DNI del alumno en la rutina
    @field_validator('dniAlumno')
    def validate_dni_length(cls, v):
        if len(v) != 8:
            raise ValueError('El DNI debe tener 8 caracteres')
        return v

class Clase(BaseModel):
    descripcion: str
    nombreProfesor: str
    emailProfesor: EmailStr
    horario: str  
    capacidad: Optional[int] = None
    alumnosInscriptos: Optional[List[str]] = []

    # Validador para la capacidad de la clase
    @field_validator('capacidad')
    def validate_capacidad(cls, v):
        if v is not None and v <= 0:
            raise ValueError('La capacidad debe ser un número positivo')
        return v

# Funciones para formatear los datos de las entidades

def individual_data_alumno(alumno: dict) -> dict:
    return {
        "id": str(alumno.get("_id", "")),
        "nombre": alumno.get("nombre", ""),
        "apellido": alumno.get("apellido", ""),
        "dni": alumno.get("dni", ""),
        "email": alumno.get("email", ""),
        "password": alumno.get("password", ""),  # Campo cambiado a 'password'
        "ingreso": alumno.get("ingreso", ""),
        "plan": alumno.get("plan", ""),
        "rol": alumno.get("rol", "alumno")
    }

def individual_data_admin(admin: dict) -> dict:
    return {
        "rol": admin.get("rol", "admin")
    }

def all_alumnos(alumnos: List[dict]) -> List[dict]:
    return [individual_data_alumno(alumno) for alumno in alumnos]

def individual_data_rutina(rutina: dict) -> dict:
    return {
        "id": str(rutina.get("_id", "")),
        "idProfesor": rutina.get("idProfesor", ""),
        "descripcion": rutina.get("descripcion", ""),
        "nombreAlumno": rutina.get("nombreAlumno", ""),
        "dniAlumno": rutina.get("dniAlumno", ""),
        "nivel": rutina.get("nivel", ""),
    }

def all_rutinas(rutinas: List[dict]) -> List[dict]:
    return [individual_data_rutina(rutina) for rutina in rutinas]

def individual_data_clase(clase: dict) -> dict:
    return {
        "id": str(clase.get("_id", "")),
        "descripcion": clase.get("descripcion", ""),
        "nombreProfesor": clase.get("nombreProfesor", ""),
        "emailProfesor": clase.get("emailProfesor", ""),
        "horario": clase.get("horario", ""),
        "capacidad": clase.get("capacidad", ""),
    }

def all_clases(clases: List[dict]) -> List[dict]:
    return [individual_data_clase(clase) for clase in clases]

def individual_data_profesor(profesor: dict) -> dict:
    return {
        "id": str(profesor.get("_id", "")),
        "nombre": profesor.get("nombre", ""),
        "apellido": profesor.get("apellido", ""),
        "dni": profesor.get("dni", ""),
        "email": profesor.get("email", ""),
        "password": profesor.get("password", ""),  # Campo cambiado a 'password'
        "ingreso": profesor.get("ingreso", ""),
    }

def all_profesores(profesores: List[dict]) -> List[dict]:
    return [individual_data_profesor(profesor) for profesor in profesores]

from fastapi import APIRouter, HTTPException
from models import Admin
from configurations import alumnos_collection,rutinas_collection,clases_collection


from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()
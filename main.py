from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import alumnos, clases, rutinas, profesores, usuarios, admins

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alumnos.router)
app.include_router(clases.router)
app.include_router(rutinas.router)
app.include_router(profesores.router)
app.include_router(usuarios.router)
app.include_router(admins.router)

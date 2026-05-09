from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routers import auth, roles, personas, usuarios, libros, copias, prestamos, detalles_prestamo

app = FastAPI(
    title="LIBRARY API",
    description="Sistema de Gestión de Biblioteca",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# CORS – Ajustar según entorno real
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "User-Agent", "X-Requested-With"],
)

# Crear tablas si no existen (solo desarrollo)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(personas.router)
app.include_router(libros.router)
app.include_router(copias.router)
app.include_router(prestamos.router)
app.include_router(detalles_prestamo.router)

@app.get("/")
def read_root():
    return {"message": "API LIBRARY - Sistema de Biblioteca"}

# Evento opcional al cerrar la app
@app.on_event("shutdown")
def shutdown_db():
    engine.dispose()
    print("Motor de base de datos cerrado.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
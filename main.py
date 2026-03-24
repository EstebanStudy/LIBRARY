from fastapi import FastAPI, Depends
from app.database.db import get_db, Base, engine
from app.routers import auth, roles, personas, usuarios, libros, copias, prestamos, detalles_prestamo
from hash_existing import hash_existing_users
from fastapi.openapi.utils import get_openapi
from app.core.dependencies import require_role
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="LIBRARY API",
    description="Sistema de Gestión de Biblioteca",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True} 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"],  # permite tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

try:
    print("Ejecutando hash_existing_users...")
    hash_existing_users()
    print("Hash de usuarios completado")
except Exception as e:
    print(f"Error al ejecutar hash_existing_users: {e}")

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

@app.get("/debug/admin")
def debug_admin(current_user = Depends(require_role("Administrador"))):
    return {"message": "¡Administrador OK!", "correo": current_user.Correo}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="LIBRARY API",
        version="1.0.0",
        description="Sistema de Biblioteca con autenticación JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Aplicar seguridad global a todos los endpoints protegidos
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
#uvicorn main:app --reload

#python -m http.server 5500
#http://localhost:5500/login.html
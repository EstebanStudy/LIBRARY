from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.persona import Persona
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_usuario(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.Id == usuario_id).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).order_by(Usuario.Id).offset(skip).limit(limit).all()

def get_usuario_by_correo(db: Session, correo: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.Correo == correo).first()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    if get_usuario_by_correo(db, usuario.Correo):
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    if db.query(Usuario).filter(Usuario.Cod_usuario == usuario.Cod_usuario).first():
        raise HTTPException(status_code=400, detail="Código de usuario ya existe")

    if not db.query(Rol).filter(Rol.Id == usuario.Rol).first():
        raise HTTPException(status_code=400, detail="Rol no existe")

    if not db.query(Persona).filter(Persona.Id == usuario.Persona).first():
        raise HTTPException(status_code=400, detail="Persona no existe")

    hashed_password = pwd_context.hash(usuario.Contraseña)

    db_usuario = Usuario(
        Cod_usuario=usuario.Cod_usuario,
        Correo=usuario.Correo,
        Contraseña=hashed_password,
        Persona=usuario.Persona,
        Rol=usuario.Rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, usuario_id: int, usuario_update: UsuarioUpdate) -> Usuario:
    db_usuario = get_usuario(db, usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = usuario_update.model_dump(exclude_unset=True)

    if "Contraseña" in update_data:
        update_data["Contraseña"] = pwd_context.hash(update_data["Contraseña"])

    if "Rol" in update_data:
        if not db.query(Rol).filter(Rol.Id == update_data["Rol"]).first():
            raise HTTPException(status_code=400, detail="Rol no existe")

    if "Persona" in update_data:
        if not db.query(Persona).filter(Persona.Id == update_data["Persona"]).first():
            raise HTTPException(status_code=400, detail="Persona no existe")

    if "Correo" in update_data and update_data["Correo"] != db_usuario.Correo:
        if get_usuario_by_correo(db, update_data["Correo"]):
            raise HTTPException(status_code=400, detail="Correo ya registrado")

    for key, value in update_data.items():
        setattr(db_usuario, key, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int) -> dict:
    db_usuario = get_usuario(db, usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}
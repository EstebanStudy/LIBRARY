from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.rol import RolCreate, RolUpdate

def get_rol(db: Session, rol_id: int) -> Rol | None:
    return db.query(Rol).filter(Rol.Id == rol_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Rol).order_by(Rol.Id).offset(skip).limit(limit).all()

def get_rol_by_nombre(db: Session, nombre: str) -> Rol | None:
    return db.query(Rol).filter(Rol.Nombre == nombre).first()

def create_rol(db: Session, rol: RolCreate) -> Rol:
    if get_rol_by_nombre(db, rol.Nombre):
        raise HTTPException(status_code=400, detail="El nombre del rol ya existe")

    db_rol = Rol(**rol.model_dump())
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

def update_rol(db: Session, rol_id: int, rol_update: RolUpdate) -> Rol:
    db_rol = get_rol(db, rol_id)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    update_data = rol_update.model_dump(exclude_unset=True)
    if "Nombre" in update_data:
        if get_rol_by_nombre(db, update_data["Nombre"]):
            raise HTTPException(status_code=400, detail="El nombre del rol ya existe")

    for key, value in update_data.items():
        setattr(db_rol, key, value)

    db.commit()
    db.refresh(db_rol)
    return db_rol

def delete_rol(db: Session, rol_id: int) -> dict:
    db_rol = get_rol(db, rol_id)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    if db.query(Usuario).filter(Usuario.Rol == rol_id).count() > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: hay usuarios asignados a este rol")

    db.delete(db_rol)
    db.commit()
    return {"message": "Rol eliminado correctamente"}
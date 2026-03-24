from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.libro import Libro
from app.schemas.libro import LibroCreate, LibroUpdate

def get_libro(db: Session, libro_id: int) -> Libro | None:
    return db.query(Libro).filter(Libro.Id == libro_id).first()

def get_libros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Libro).order_by(Libro.Id).offset(skip).limit(limit).all()

def get_libro_by_cod(db: Session, cod_libro: int) -> Libro | None:
    return db.query(Libro).filter(Libro.Cod_libro == cod_libro).first()

def create_libro(db: Session, libro: LibroCreate) -> Libro:
    if get_libro_by_cod(db, libro.Cod_libro):
        raise HTTPException(status_code=400, detail="Código de libro ya existe")

    db_libro = Libro(**libro.model_dump())
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def update_libro(db: Session, libro_id: int, libro_update: LibroUpdate) -> Libro:
    db_libro = get_libro(db, libro_id)
    if not db_libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    update_data = libro_update.model_dump(exclude_unset=True)

    if "Cod_libro" in update_data and update_data["Cod_libro"] != db_libro.Cod_libro:
        if get_libro_by_cod(db, update_data["Cod_libro"]):
            raise HTTPException(status_code=400, detail="Código de libro ya existe")

    for key, value in update_data.items():
        setattr(db_libro, key, value)
    
    db.commit()
    db.refresh(db_libro)
    return db_libro

def delete_libro(db: Session, libro_id: int) -> dict:
    db_libro = get_libro(db, libro_id)
    if not db_libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    db.delete(db_libro)
    db.commit()
    return {"message": "Libro eliminado correctamente"}
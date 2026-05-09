from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.libro import Libro
from app.models.copia import Copia
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

    copias_asociadas = db.query(Copia).filter(Copia.Libro == libro_id).count()
    if copias_asociadas > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el libro porque tiene copias asociadas. Elimina o reasigna las copias primero."
        )

    db.delete(db_libro)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo eliminar el libro debido a relaciones existentes. Elimina o desvincula las entidades relacionadas primero."
        )
    return {"message": "Libro eliminado correctamente"}

def buscar_libros(db: Session, query: str = None, skip: int = 0, limit: int = 100):
    """Busca libros por título o autor."""
    from sqlalchemy import or_
    
    q = db.query(Libro)
    
    if query:
        # Buscar en título o autor (ignorando mayúsculas/minúsculas)
        search = f"%{query}%"
        q = q.filter(
            or_(
                Libro.Nombre_libro.ilike(search),
                Libro.Autor.ilike(search)
            )
        )
    
    return q.order_by(Libro.Nombre_libro).offset(skip).limit(limit).all()
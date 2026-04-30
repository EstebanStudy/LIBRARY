from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.copia import Copia
from app.models.libro import Libro
from app.schemas.copia import CopiaCreate, CopiaUpdate

def get_copia(db: Session, copia_id: int) -> Copia | None:
    return db.query(Copia).options(joinedload(Copia.libro_rel)).filter(Copia.Id == copia_id).first()

def get_copias(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Copia).options(joinedload(Copia.libro_rel)).order_by(Copia.Id).offset(skip).limit(limit).all()

def get_copias_by_libro(db: Session, libro_id: int):
    return db.query(Copia).options(joinedload(Copia.libro_rel)).filter(Copia.Libro == libro_id).all()

def create_copia(db: Session, copia: CopiaCreate) -> Copia:
    libro = db.query(Libro).filter(Libro.Id == copia.Libro).first()
    if not libro:
        raise HTTPException(status_code=400, detail="Libro no existe")

    db_copia = Copia(**copia.model_dump())
    db.add(db_copia)
    db.commit()
    db.refresh(db_copia)
    # Recargar con relación para la respuesta
    db.refresh(db_copia, attribute_names=["libro_rel"])
    return db_copia

def update_copia(db: Session, copia_id: int, copia_update: CopiaUpdate) -> Copia:
    db_copia = get_copia(db, copia_id)
    if not db_copia:
        raise HTTPException(status_code=404, detail="Copia no encontrada")

    update_data = copia_update.model_dump(exclude_unset=True)

    if "Libro" in update_data:
        libro = db.query(Libro).filter(Libro.Id == update_data["Libro"]).first()
        if not libro:
            raise HTTPException(status_code=400, detail="Libro no existe")

    for key, value in update_data.items():
        setattr(db_copia, key, value)

    db.commit()
    db.refresh(db_copia)
    db.refresh(db_copia, attribute_names=["libro_rel"])
    return db_copia

def delete_copia(db: Session, copia_id: int) -> dict:
    db_copia = get_copia(db, copia_id)
    if not db_copia:
        raise HTTPException(status_code=404, detail="Copia no encontrada")

    db.delete(db_copia)
    db.commit()
    return {"message": "Copia eliminada correctamente"}
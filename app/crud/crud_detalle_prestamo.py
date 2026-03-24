from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.detalle_prestamo import DetallePrestamo
from app.models.copia import Copia
from app.models.prestamo import Prestamo
from app.schemas.detalle_prestamo import DetallePrestamoCreate, DetallePrestamoUpdate

def get_detalle(db: Session, detalle_id: int) -> DetallePrestamo | None:
    return db.query(DetallePrestamo).filter(DetallePrestamo.Id == detalle_id).first()

def get_detalles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DetallePrestamo).order_by(DetallePrestamo.Id).offset(skip).limit(limit).all()

def get_detalles_by_prestamo(db: Session, prestamo_id: int):
    return db.query(DetallePrestamo).filter(DetallePrestamo.Prestamo == prestamo_id).all()

def create_detalle(db: Session, detalle: DetallePrestamoCreate) -> DetallePrestamo:
    prestamo = db.query(Prestamo).filter(Prestamo.Id == detalle.Prestamo).first()
    if not prestamo:
        raise HTTPException(status_code=400, detail="Préstamo no existe")

    copia = db.query(Copia).filter(Copia.Id == detalle.Copia).first()
    if not copia:
        raise HTTPException(status_code=400, detail="Copia no existe")
    if not copia.Disponible:
        raise HTTPException(status_code=400, detail="La copia no está disponible")

    db_detalle = DetallePrestamo(**detalle.model_dump())
    db.add(db_detalle)

    copia.Disponible = False

    db.commit()
    db.refresh(db_detalle)
    return db_detalle

def update_detalle(db: Session, detalle_id: int, detalle_update: DetallePrestamoUpdate) -> DetallePrestamo:
    db_detalle = get_detalle(db, detalle_id)
    if not db_detalle:
        raise HTTPException(status_code=404, detail="Detalle de préstamo no encontrado")

    update_data = detalle_update.model_dump(exclude_unset=True)

    if "Copia" in update_data and update_data["Copia"] != db_detalle.Copia:
        nueva_copia = db.query(Copia).filter(Copia.Id == update_data["Copia"]).first()
        if not nueva_copia:
            raise HTTPException(status_code=400, detail="Nueva copia no existe")
        if not nueva_copia.Disponible:
            raise HTTPException(status_code=400, detail="Nueva copia no disponible")
        
        copia_anterior = db.query(Copia).filter(Copia.Id == db_detalle.Copia).first()
        if copia_anterior:
            copia_anterior.Disponible = True

        nueva_copia.Disponible = False

    for key, value in update_data.items():
        setattr(db_detalle, key, value)

    db.commit()
    db.refresh(db_detalle)
    return db_detalle

def delete_detalle(db: Session, detalle_id: int) -> dict:
    db_detalle = get_detalle(db, detalle_id)
    if not db_detalle:
        raise HTTPException(status_code=404, detail="Detalle de préstamo no encontrado")

    copia = db.query(Copia).filter(Copia.Id == db_detalle.Copia).first()
    if copia:
        copia.Disponible = True

    db.delete(db_detalle)
    db.commit()
    return {"message": "Detalle de préstamo eliminado correctamente"}
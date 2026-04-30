from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.prestamo import Prestamo
from app.models.detalle_prestamo import DetallePrestamo
from app.models.copia import Copia
from app.models.usuario import Usuario
from app.schemas.prestamo import PrestamoCreate, PrestamoUpdate, DetallePrestamoCreate
from app.models.persona import Persona
from sqlalchemy.orm import joinedload

def get_prestamo(db: Session, prestamo_id: int) -> Prestamo | None:
    return db.query(Prestamo).options(
        joinedload(Prestamo.usuario_rel).joinedload(Usuario.persona_rel)
    ).filter(Prestamo.Id == prestamo_id).first()

def get_prestamos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Prestamo).options(
        joinedload(Prestamo.usuario_rel).joinedload(Usuario.persona_rel),  # ← clave
        joinedload(Prestamo.detalles)
    ).order_by(Prestamo.Id).offset(skip).limit(limit).all()

def get_prestamos_by_usuario(db: Session, usuario_id: int):
    return db.query(Prestamo).filter(Prestamo.Usuario == usuario_id).all()

def create_prestamo(db: Session, prestamo: PrestamoCreate) -> Prestamo:
    usuario = db.query(Usuario).filter(Usuario.Id == prestamo.Usuario).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    db_prestamo = Prestamo(Usuario=prestamo.Usuario)
    db.add(db_prestamo)
    db.flush() 

    for detalle_in in prestamo.detalles:
        copia = db.query(Copia).filter(Copia.Id == detalle_in.Copia).first()
        if not copia:
            raise HTTPException(status_code=400, detail=f"Copia {detalle_in.Copia} no existe")
        if not copia.Disponible:
            raise HTTPException(status_code=400, detail=f"Copia {detalle_in.Copia} no está disponible")

        db_detalle = DetallePrestamo(
            Prestamo=db_prestamo.Id,
            Copia=detalle_in.Copia,
            Fecha_entrega_esperada=detalle_in.Fecha_entrega_esperada
        )
        db.add(db_detalle)

        copia.Disponible = False

    db.commit()
    db.refresh(db_prestamo)
    return db_prestamo

def update_prestamo(db: Session, prestamo_id: int, prestamo_update: PrestamoUpdate) -> Prestamo:
    db_prestamo = get_prestamo(db, prestamo_id)
    if not db_prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    if prestamo_update.Usuario:
        usuario = db.query(Usuario).filter(Usuario.Id == prestamo_update.Usuario).first()
        if not usuario:
            raise HTTPException(status_code=400, detail="Usuario no existe")
        db_prestamo.Usuario = prestamo_update.Usuario

    db.commit()
    db.refresh(db_prestamo)
    return db_prestamo

def delete_prestamo(db: Session, prestamo_id: int) -> dict:
    db_prestamo = get_prestamo(db, prestamo_id)
    if not db_prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    no_devuelto = [detalle for detalle in db_prestamo.detalles if detalle.Fecha_devolucion_real is None]
    if no_devuelto:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el préstamo porque contiene registros vinculados. Por favor, completa o cancela el flujo antes de borrar."
        )

    for detalle in db_prestamo.detalles:
        copia = db.query(Copia).filter(Copia.Id == detalle.Copia).first()
        if copia:
            copia.Disponible = True

    db.delete(db_prestamo)
    db.commit()
    return {"message": "Préstamo eliminado correctamente"}

def devolver_prestamo(db: Session, prestamo_id: int, copia_id: int = None) -> Prestamo:
    """Marca uno o todos los ejemplares de un préstamo como devueltos."""
    db_prestamo = get_prestamo(db, prestamo_id)
    if not db_prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    detalles_a_devolver = []
    if copia_id:
        # Devolver una copia específica
        for detalle in db_prestamo.detalles:
            if detalle.Copia == copia_id and detalle.Fecha_devolucion_real is None:
                detalles_a_devolver.append(detalle)
        if not detalles_a_devolver:
            raise HTTPException(status_code=400, detail="La copia ya está devuelta o no pertenece a este préstamo")
    else:
        # Devolver todas las copias
        for detalle in db_prestamo.detalles:
            if detalle.Fecha_devolucion_real is None:
                detalles_a_devolver.append(detalle)

    from datetime import date
    fecha_actual = date.today()

    for detalle in detalles_a_devolver:
        detalle.Fecha_devolucion_real = fecha_actual
        # Marcar copia como disponible
        copia = db.query(Copia).filter(Copia.Id == detalle.Copia).first()
        if copia:
            copia.Disponible = True

    db.commit()
    db.refresh(db_prestamo)
    return db_prestamo
    return {"message": "Préstamo eliminado correctamente"}
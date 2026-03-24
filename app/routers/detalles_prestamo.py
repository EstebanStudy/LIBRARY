from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.detalle_prestamo import (
    DetallePrestamoCreate, DetallePrestamoUpdate, DetallePrestamoResponse
)
from app.crud.crud_detalle_prestamo import (
    get_detalle, get_detalles, create_detalle, update_detalle, delete_detalle,
    get_detalles_by_prestamo
)
from app.core.dependencies import require_role

router = APIRouter(prefix="/detalles-prestamo", tags=["detalles-prestamo"])

@router.get("/", response_model=List[DetallePrestamoResponse])
def read_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_detalles(db, skip=skip, limit=limit)

@router.get("/{detalle_id}", response_model=DetallePrestamoResponse)
def read_detalle(detalle_id: int, db: Session = Depends(get_db)):
    db_detalle = get_detalle(db, detalle_id)
    if db_detalle is None:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return db_detalle

@router.get("/prestamo/{prestamo_id}", response_model=List[DetallePrestamoResponse])
def read_detalles_by_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    return get_detalles_by_prestamo(db, prestamo_id)

@router.post("/", response_model=DetallePrestamoResponse, status_code=201)
def create_new_detalle(
    detalle: DetallePrestamoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_detalle(db=db, detalle=detalle)

@router.put("/{detalle_id}", response_model=DetallePrestamoResponse)
def update_existing_detalle(
    detalle_id: int,
    detalle: DetallePrestamoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_detalle(db=db, detalle_id=detalle_id, detalle_update=detalle)

@router.delete("/{detalle_id}")
def delete_existing_detalle(
    detalle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_detalle(db=db, detalle_id=detalle_id)
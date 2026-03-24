from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.prestamo import PrestamoCreate, PrestamoUpdate, PrestamoResponse
from app.crud.crud_prestamo import (
    get_prestamo, get_prestamos, create_prestamo, update_prestamo, delete_prestamo,
    get_prestamos_by_usuario
)
from app.core.dependencies import require_any_role, get_current_active_user

router = APIRouter(prefix="/prestamos", tags=["prestamos"])

@router.get("/", response_model=List[PrestamoResponse])
def read_prestamos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return get_prestamos(db, skip=skip, limit=limit)

@router.get("/{prestamo_id}", response_model=PrestamoResponse)
def read_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    db_prestamo = get_prestamo(db, prestamo_id)
    if db_prestamo is None:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return db_prestamo

@router.get("/usuario/{usuario_id}", response_model=List[PrestamoResponse])
def read_prestamos_by_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return get_prestamos_by_usuario(db, usuario_id)

@router.post("/", response_model=PrestamoResponse, status_code=201)
def create_new_prestamo(
    prestamo: PrestamoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_role(["Administrador", "Usuario", "Niños"]))  # <- aquí
):
    return create_prestamo(db=db, prestamo=prestamo)

@router.put("/{prestamo_id}", response_model=PrestamoResponse)
def update_existing_prestamo(
    prestamo_id: int,
    prestamo: PrestamoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_role(["Administrador"]))  # solo admin puede editar
):
    return update_prestamo(db=db, prestamo_id=prestamo_id, prestamo_update=prestamo)

@router.delete("/{prestamo_id}")
def delete_existing_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_any_role(["Administrador"]))  # solo admin puede eliminar
):
    return delete_prestamo(db=db, prestamo_id=prestamo_id)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.copia import CopiaCreate, CopiaUpdate, CopiaResponse
from app.crud.crud_copia import (
    get_copia, get_copias, create_copia, update_copia, delete_copia,
    get_copias_by_libro
)
from app.core.dependencies import require_role

router = APIRouter(prefix="/copias", tags=["copias"])

@router.get("/", response_model=List[CopiaResponse])
def read_copias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_copias(db, skip=skip, limit=limit)

@router.get("/{copia_id}", response_model=CopiaResponse)
def read_copia(copia_id: int, db: Session = Depends(get_db)):
    db_copia = get_copia(db, copia_id)
    if db_copia is None:
        raise HTTPException(status_code=404, detail="Copia no encontrada")
    return db_copia

@router.get("/libro/{libro_id}", response_model=List[CopiaResponse])
def read_copias_by_libro(libro_id: int, db: Session = Depends(get_db)):
    return get_copias_by_libro(db, libro_id)

@router.post("/", response_model=CopiaResponse, status_code=201)
def create_new_copia(
    copia: CopiaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_copia(db=db, copia=copia)

@router.put("/{copia_id}", response_model=CopiaResponse)
def update_existing_copia(
    copia_id: int,
    copia: CopiaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_copia(db=db, copia_id=copia_id, copia_update=copia)

@router.delete("/{copia_id}")
def delete_existing_copia(
    copia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_copia(db=db, copia_id=copia_id)
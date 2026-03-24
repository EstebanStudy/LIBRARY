from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.crud.crud_rol import (
    get_rol, get_roles, create_rol, update_rol, delete_rol
)
from app.core.dependencies import require_role  # ← restricción aquí

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RolResponse, status_code=201)
def create_new_rol(
    rol: RolCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_rol(db=db, rol=rol)

@router.get("/", response_model=List[RolResponse])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return get_roles(db, skip=skip, limit=limit)

@router.get("/{rol_id}", response_model=RolResponse)
def read_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    db_rol = get_rol(db, rol_id)
    if db_rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return db_rol

@router.put("/{rol_id}", response_model=RolResponse)
def update_existing_rol(
    rol_id: int,
    rol: RolUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_rol(db=db, rol_id=rol_id, rol_update=rol)

@router.delete("/{rol_id}")
def delete_existing_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_rol(db=db, rol_id=rol_id)
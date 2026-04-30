# app/routers/usuarios.py  ← REEMPLAZA TODO
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.crud.crud_usuario import get_usuario, get_usuarios, create_usuario, update_usuario, delete_usuario
from app.core.dependencies import require_role, get_current_active_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("/", response_model=List[UsuarioResponse])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_usuarios(db, skip=skip, limit=limit)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

@router.post("/", response_model=UsuarioResponse, status_code=201)
def create_new_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_usuario(db=db, usuario=usuario)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_existing_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_usuario(db=db, usuario_id=usuario_id, usuario_update=usuario)

@router.delete("/{usuario_id}")
def delete_existing_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_usuario(db=db, usuario_id=usuario_id)
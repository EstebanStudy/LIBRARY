# app/routers/libros.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.libro import LibroCreate, LibroUpdate, LibroResponse
from app.crud.crud_libro import get_libro, get_libros, create_libro, update_libro, delete_libro
from app.core.dependencies import require_role, get_current_active_user

router = APIRouter(prefix="/libros", tags=["libros"])

@router.get("/", response_model=List[LibroResponse])
def read_libros(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    libros = get_libros(db, skip=skip, limit=limit)

    # FILTRO CORRECTO PARA NIÑOS
    if current_user.rol_rel and current_user.rol_rel.Nombre == "Niños":
        libros = [libro for libro in libros if libro.Es_Infantil == True]

    return libros

@router.get("/{libro_id}", response_model=LibroResponse)
def read_libro(
    libro_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # Opcional: si quieres que todos los usuarios autenticados puedan ver un libro
):
    libro = get_libro(db, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

# === SOLO ADMINISTRADOR ===
@router.post("/", response_model=LibroResponse, status_code=201)
def create_new_libro(
    libro: LibroCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_libro(db=db, libro=libro)

@router.put("/{libro_id}", response_model=LibroResponse)
def update_existing_libro(
    libro_id: int,
    libro: LibroUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_libro(db=db, libro_id=libro_id, libro_update=libro)

@router.delete("/{libro_id}")
def delete_existing_libro(
    libro_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_libro(db=db, libro_id=libro_id)
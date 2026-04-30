from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from app.crud.crud_persona import (
    get_persona, get_personas, create_persona, update_persona, delete_persona
)
from app.core.dependencies import require_role

router = APIRouter(prefix="/personas", tags=["personas"])

@router.get("/", response_model=List[PersonaResponse])
def read_personas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_personas(db, skip=skip, limit=limit)

@router.get("/{persona_id}", response_model=PersonaResponse)
def read_persona(persona_id: int, db: Session = Depends(get_db)):
    db_persona = get_persona(db, persona_id)
    if db_persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db_persona

@router.post("/", response_model=PersonaResponse, status_code=201)
def create_new_persona(
    persona: PersonaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return create_persona(db=db, persona=persona)

@router.put("/{persona_id}", response_model=PersonaResponse)
def update_existing_persona(
    persona_id: int,
    persona: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return update_persona(db=db, persona_id=persona_id, persona_update=persona)

@router.delete("/{persona_id}")
def delete_existing_persona(
    persona_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Administrador"))
):
    return delete_persona(db=db, persona_id=persona_id)
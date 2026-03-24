from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaUpdate

def get_persona(db: Session, persona_id: int) -> Persona | None:
    return db.query(Persona).filter(Persona.Id == persona_id).first()

def get_personas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Persona).order_by(Persona.Id).offset(skip).limit(limit).all()

def get_persona_by_cedula(db: Session, cedula: str) -> Persona | None:
    return db.query(Persona).filter(Persona.Cedula == cedula).first()

def create_persona(db: Session, persona: PersonaCreate) -> Persona:
    if get_persona_by_cedula(db, persona.Cedula):
        raise HTTPException(status_code=400, detail="Cédula ya existe")

    db_persona = Persona(**persona.model_dump())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

def update_persona(db: Session, persona_id: int, persona_update: PersonaUpdate) -> Persona:
    db_persona = get_persona(db, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    update_data = persona_update.model_dump(exclude_unset=True)

    if "Cedula" in update_data and update_data["Cedula"] != db_persona.Cedula:
        if get_persona_by_cedula(db, update_data["Cedula"]):
            raise HTTPException(status_code=400, detail="Cédula ya existe")

    for key, value in update_data.items():
        setattr(db_persona, key, value)

    db.commit()
    db.refresh(db_persona)
    return db_persona

def delete_persona(db: Session, persona_id: int) -> dict:
    db_persona = get_persona(db, persona_id)
    if not db_persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    db.delete(db_persona)
    db.commit()
    return {"message": "Persona eliminada correctamente"}
from pydantic import BaseModel, Field
from typing import Optional

class PersonaBase(BaseModel):
    Cedula: str = Field(..., min_length=1, max_length=20)
    Nombre: str = Field(..., min_length=1, max_length=100)
    Telefono: Optional[str] = Field(None, max_length=20)

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    Cedula: Optional[str] = Field(None, min_length=1, max_length=20)
    Nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    Telefono: Optional[str] = Field(None, max_length=20)

class PersonaResponse(PersonaBase):
    Id: int

    class ConfigDict:
        from_attributes = True
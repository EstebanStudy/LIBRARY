from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.schemas.persona import PersonaResponse

class UsuarioBase(BaseModel):
    Cod_usuario: int = Field(..., gt=0)
    Correo: EmailStr

class UsuarioCreate(UsuarioBase):
    Contraseña: str = Field(..., min_length=8)
    Persona: int = Field(..., gt=0)
    Rol: int = Field(..., gt=0)

class UsuarioUpdate(BaseModel):
    Cod_usuario: Optional[int] = None
    Correo: Optional[EmailStr] = None
    Contraseña: Optional[str] = Field(None, min_length=8)
    Persona: Optional[int] = None
    Rol: Optional[int] = None

class UsuarioResponse(BaseModel):
    Id: int
    Cod_usuario: int
    Correo: str
    Persona: int
    Rol: int
    persona_rel: Optional[PersonaResponse] = None   # <-- agregar esta línea

    class ConfigDict:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.libro import LibroResponse  # Importamos el schema del libro

class CopiaBase(BaseModel):
    Libro: int = Field(..., gt=0)
    Notas: Optional[str] = Field(None, max_length=255)
    Disponible: bool = True

class CopiaCreate(CopiaBase):
    pass

class CopiaUpdate(BaseModel):
    Libro: Optional[int] = None
    Notas: Optional[str] = Field(None, max_length=255)
    Disponible: Optional[bool] = None

class CopiaResponse(CopiaBase):
    Id: int
    libro_rel: Optional[LibroResponse] = None   # <-- AÑADIR ESTA LÍNEA

    class ConfigDict:
        from_attributes = True
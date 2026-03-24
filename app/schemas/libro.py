from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class LibroBase(BaseModel):
    Cod_libro: int = Field(..., gt=0)
    Nombre_libro: str = Field(..., min_length=1, max_length=200)
    Fecha_publicacion: Optional[date] = None
    Autor: Optional[str] = Field(None, max_length=100)
    Portada_Url: Optional[str] = None

class LibroCreate(LibroBase):
    pass

class LibroUpdate(BaseModel):
    Cod_libro: Optional[int] = None
    Nombre_libro: Optional[str] = Field(None, min_length=1, max_length=200)
    Fecha_publicacion: Optional[date] = None
    Autor: Optional[str] = Field(None, max_length=100)
    Portada_Url: Optional[str] = None

class LibroResponse(LibroBase):
    Id: int
    Es_Infantil: bool 

    class ConfigDict:
        from_attributes = True
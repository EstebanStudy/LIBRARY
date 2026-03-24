from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.schemas.usuario import UsuarioResponse

class DetallePrestamoBase(BaseModel):
    Copia: int = Field(..., gt=0)
    Fecha_entrega_esperada: date

class DetallePrestamoCreate(DetallePrestamoBase):
    pass

class DetallePrestamoResponse(DetallePrestamoBase):
    Id: int
    Fecha_devolucion_real: Optional[date] = None

    class ConfigDict:
        from_attributes = True

class PrestamoBase(BaseModel):
    Usuario: int = Field(..., gt=0)

class PrestamoCreate(PrestamoBase):
    detalles: List[DetallePrestamoCreate] = Field(..., min_items=1)

class PrestamoUpdate(BaseModel):
    Usuario: Optional[int] = None

class PrestamoResponse(PrestamoBase):
    Id: int
    Fecha_prestamo: datetime
    detalles: List[DetallePrestamoResponse] = []
    # AGREGA ESTA LÍNEA:
    usuario_rel: Optional[UsuarioResponse] = None 

    class ConfigDict:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class DetallePrestamoBase(BaseModel):
    Prestamo: int = Field(..., gt=0)
    Copia: int = Field(..., gt=0)
    Fecha_entrega_esperada: date

class DetallePrestamoCreate(DetallePrestamoBase):
    pass

class DetallePrestamoUpdate(BaseModel):
    Prestamo: Optional[int] = None
    Copia: Optional[int] = None
    Fecha_entrega_esperada: Optional[date] = None
    Fecha_devolucion_real: Optional[date] = None

class DetallePrestamoResponse(DetallePrestamoBase):
    Id: int
    Fecha_devolucion_real: Optional[date] = None

    class ConfigDict:
        from_attributes = True
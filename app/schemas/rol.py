from pydantic import BaseModel, Field
from typing import Optional

class RolBase(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=50)

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    Nombre: Optional[str] = Field(None, min_length=1, max_length=50)

class RolResponse(RolBase):
    Id: int

    class ConfigDict:
        from_attributes = True
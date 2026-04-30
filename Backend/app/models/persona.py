from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base

class Persona(Base):
    __tablename__ = "Personas"
    __table_args__ = {"implicit_returning": False}

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Cedula = Column(String(20), unique=True, nullable=False, index=True)
    Nombre = Column(String(100), nullable=False)
    Telefono = Column(String(20), nullable=True)
    Direccion = Column(String(255), nullable=True)

    usuarios = relationship("Usuario", back_populates="persona_rel")
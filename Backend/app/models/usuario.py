from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, VARBINARY
from app.database.db import Base

class Usuario(Base):
    __tablename__ = "Usuarios"
    __table_args__ = {"implicit_returning": False}

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Cod_usuario = Column(Integer, unique=True, nullable=False)
    Correo = Column(String(255), nullable=False, unique=True)
    Salt = Column(UNIQUEIDENTIFIER, nullable=False)
    PasswordHash = Column(VARBINARY(32), nullable=False)
    Persona = Column(Integer, ForeignKey("Personas.Id"), nullable=False)
    Rol = Column(Integer, ForeignKey("Roles.Id"), nullable=False)

    persona_rel = relationship("Persona", back_populates="usuarios")
    rol_rel = relationship("Rol", lazy="joined")